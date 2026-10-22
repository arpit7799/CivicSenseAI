"""Explainable geographic, category, time, and text duplicate scoring."""

from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
import re

from app.contracts.civic_record import ComplaintObservation
from app.contracts.duplicate import DuplicateResult
from app.core.complaint_repository import ComplaintQuery, ComplaintRepository
from app.core.interfaces import DuplicateDetector


class CivicDuplicateDetector(DuplicateDetector):
    def __init__(
        self,
        repository: ComplaintRepository,
        *,
        radius_meters: float = 250.0,
        time_window_days: int = 30,
        duplicate_threshold: float = 0.70,
        clock=None,
    ):
        self.repository = repository
        self.radius_meters = radius_meters
        self.time_window_days = time_window_days
        self.duplicate_threshold = duplicate_threshold
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    async def check(
        self,
        issue_type: str,
        latitude: float,
        longitude: float,
        description: str | None = None,
        image_url: str | None = None,
    ) -> DuplicateResult:
        del image_url  # Image similarity is intentionally deferred until an image index exists.
        now = self._clock()
        issue = issue_type.strip().casefold()
        candidates = await self.repository.list_complaints(
            ComplaintQuery(
                start_at=now - timedelta(days=self.time_window_days),
                end_at=now,
                issue_type=issue,
                latitude=latitude,
                longitude=longitude,
                radius_meters=self.radius_meters,
            )
        )

        best: tuple[float, ComplaintObservation, float] | None = None
        for record in candidates:
            if record.issue_type.strip().casefold() != issue:
                continue
            distance = haversine_meters(latitude, longitude, record.latitude, record.longitude)
            if distance > self.radius_meters:
                continue
            age = max(0.0, (now - record.reported_at).total_seconds())
            if age > self.time_window_days * 86400:
                continue
            proximity_score = max(0.0, 1.0 - distance / self.radius_meters)
            recency_score = max(0.0, 1.0 - age / (self.time_window_days * 86400))
            text_score = text_similarity(description, record.description)
            if text_score is None:
                score = 0.55 * proximity_score + 0.25 * recency_score
            else:
                score = 0.55 * proximity_score + 0.20 * recency_score + 0.25 * text_score
            if best is None or score > best[0]:
                best = (score, record, text_score or 0.0)

        if best is None:
            return DuplicateResult(
                is_potential_duplicate=False,
                similarity_score=0.0,
                match_factors=[],
                source="duplicate_engine_v1",
            )

        score, record, text_score = best
        factors = ["same_issue_type", "gps_proximity", "reported_within_time_window"]
        if text_score >= 0.45:
            factors.append("description_similarity")
        return DuplicateResult(
            is_potential_duplicate=score >= self.duplicate_threshold,
            existing_complaint_id=record.complaint_id if score >= self.duplicate_threshold else None,
            similarity_score=round(min(1.0, max(0.0, score)), 3),
            match_factors=factors,
            source="duplicate_engine_v1",
        )


def text_similarity(left: str | None, right: str | None) -> float | None:
    if not left or not right:
        return None
    left_norm = normalize_text(left)
    right_norm = normalize_text(right)
    if not left_norm or not right_norm:
        return None
    left_tokens, right_tokens = set(left_norm.split()), set(right_norm.split())
    union = left_tokens | right_tokens
    jaccard = len(left_tokens & right_tokens) / len(union) if union else 0.0
    sequence = SequenceMatcher(None, left_norm, right_norm).ratio()
    return max(jaccard, sequence)


def normalize_text(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.casefold()))


def haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two WGS84 coordinates."""
    from math import asin, cos, radians, sin, sqrt

    lat1_r, lat2_r = radians(lat1), radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)
    a = sin(delta_lat / 2) ** 2 + cos(lat1_r) * cos(lat2_r) * sin(delta_lon / 2) ** 2
    return 6_371_000 * 2 * asin(sqrt(min(1.0, a)))
