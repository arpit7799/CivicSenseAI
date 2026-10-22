"""Reverse geocoding through a configurable Nominatim-compatible service.

The public OpenStreetMap Nominatim endpoint is intended only for low-volume,
user-triggered lookups. This adapter caches coordinates in process, spaces
requests at least one second apart, sends an identifying User-Agent, and
returns attribution with every result. Production deployments should configure
a provider appropriate to their traffic and service terms.
"""

import asyncio
from time import monotonic

import httpx

from app.config import get_settings
from app.contracts.location import Coordinates, LocationResult
from app.core.errors import ProviderUnavailableError
from app.core.interfaces import LocationProvider


class NominatimLocationProvider(LocationProvider):
    """Resolve WGS84 coordinates into normalized address fields."""

    ATTRIBUTION = "© OpenStreetMap contributors"
    MIN_REQUEST_INTERVAL_SECONDS = 1.0
    MAX_CACHE_ENTRIES = 10_000

    def __init__(
        self,
        *,
        client: httpx.AsyncClient | None = None,
        min_request_interval_seconds: float = MIN_REQUEST_INTERVAL_SECONDS,
    ):
        self.settings = get_settings()
        self._client = client
        self._min_request_interval_seconds = max(0.0, min_request_interval_seconds)
        self._last_request_at: float | None = None
        self._request_lock = asyncio.Lock()
        self._resolve_lock = asyncio.Lock()
        self._cache: dict[tuple[float, float], tuple[float, LocationResult]] = {}

    async def resolve(self, latitude: float, longitude: float) -> LocationResult:
        coordinates = Coordinates(latitude=latitude, longitude=longitude)
        cache_key = (round(latitude, 5), round(longitude, 5))
        async with self._resolve_lock:
            cached = self._cache.get(cache_key)
            now = monotonic()
            if cached and cached[0] > now:
                return cached[1].model_copy(deep=True, update={"coordinates": coordinates})

            payload = await self._reverse(latitude, longitude)
            result = self._to_location_result(payload, coordinates)
            ttl = self.settings.geocoder_cache_ttl_seconds
            if ttl > 0:
                self._purge_expired_cache()
                if len(self._cache) >= self.MAX_CACHE_ENTRIES:
                    self._cache.pop(next(iter(self._cache)))
                self._cache[cache_key] = (monotonic() + ttl, result)
            return result.model_copy(deep=True)

    def _purge_expired_cache(self) -> None:
        now = monotonic()
        expired_keys = [key for key, (expires_at, _) in self._cache.items() if expires_at <= now]
        for key in expired_keys:
            self._cache.pop(key, None)

    async def _reverse(self, latitude: float, longitude: float) -> dict:
        async with self._request_lock:
            if self._last_request_at is not None:
                elapsed = monotonic() - self._last_request_at
                wait_seconds = self._min_request_interval_seconds - elapsed
                if wait_seconds > 0:
                    await asyncio.sleep(wait_seconds)
            self._last_request_at = monotonic()

        url = f"{self.settings.geocoder_base_url.rstrip('/')}/reverse"
        params = {
            "lat": latitude,
            "lon": longitude,
            "format": "jsonv2",
            "addressdetails": 1,
        }
        headers = {"User-Agent": self.settings.geocoder_user_agent}

        try:
            if self._client is not None:
                response = await self._client.get(url, params=params, headers=headers)
                response.raise_for_status()
                payload = response.json()
                if not isinstance(payload, dict):
                    raise ValueError("Geocoder returned a non-object response")
                return payload

            async with httpx.AsyncClient(
                timeout=self.settings.geocoder_timeout_seconds,
                headers=headers,
            ) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                payload = response.json()
                if not isinstance(payload, dict):
                    raise ValueError("Geocoder returned a non-object response")
                return payload
        except (httpx.HTTPError, ValueError) as exc:
            raise ProviderUnavailableError("nominatim", str(exc)) from exc

    def _to_location_result(
        self,
        payload: dict,
        coordinates: Coordinates,
    ) -> LocationResult:
        address_fields = payload.get("address")
        if not isinstance(address_fields, dict):
            address_fields = {}
        city = self._first(address_fields, "city", "town", "village", "municipality", "city_district")
        district = self._first(address_fields, "state_district", "district", "county")
        state = self._first(address_fields, "state")
        address = payload.get("display_name") or None
        # Nominatim does not provide a location-confidence score. This is a
        # transparent completeness heuristic, capped below full confidence.
        confidence = (
            (0.25 if address else 0.0)
            + (0.20 if city else 0.0)
            + (0.20 if district else 0.0)
            + (0.20 if state else 0.0)
        )
        confidence = round(confidence, 2)

        return LocationResult(
            address=address,
            city=city,
            district=district,
            state=state,
            ward=self._first(address_fields, "neighbourhood", "suburb", "quarter"),
            zone=self._first(address_fields, "borough", "city_district"),
            pincode=self._first(address_fields, "postcode"),
            coordinates=coordinates,
            confidence=confidence,
            source="nominatim",
            attribution=self.ATTRIBUTION,
        )

    @staticmethod
    def _first(values: dict, *keys: str) -> str | None:
        for key in keys:
            value = values.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None
