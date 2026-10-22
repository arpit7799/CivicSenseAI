"""PostGIS-backed complaint read projection using asyncpg."""

from app.config import get_settings
from app.contracts.civic_record import ComplaintObservation
from app.core.complaint_repository import ComplaintQuery
from app.core.errors import ProviderUnavailableError


class PostgresComplaintRepository:
    def __init__(self, *, pool=None, database_url: str | None = None):
        self._pool = pool
        self._database_url = database_url or get_settings().database_url

    async def _get_pool(self):
        if self._pool is None:
            try:
                import asyncpg

                self._pool = await asyncpg.create_pool(self._database_url, min_size=1, max_size=5)
            except Exception as exc:
                raise ProviderUnavailableError("complaint_database", str(exc)) from exc
        return self._pool

    async def upsert_observations(self, records: list[ComplaintObservation]) -> int:
        if not records:
            return 0
        pool = await self._get_pool()
        sql = """
            INSERT INTO civic_complaint_index (
                complaint_id, issue_type, reported_at, latitude, longitude,
                severity, description, image_ref, city, district, state, ward, zone
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13
            )
            ON CONFLICT (complaint_id) DO UPDATE SET
                issue_type = EXCLUDED.issue_type,
                reported_at = EXCLUDED.reported_at,
                latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude,
                severity = EXCLUDED.severity,
                description = EXCLUDED.description,
                image_ref = EXCLUDED.image_ref,
                city = EXCLUDED.city,
                district = EXCLUDED.district,
                state = EXCLUDED.state,
                ward = EXCLUDED.ward,
                zone = EXCLUDED.zone,
                updated_at = now()
        """
        values = [
            (
                r.complaint_id, r.issue_type, r.reported_at, r.latitude, r.longitude,
                r.severity, r.description, r.image_ref, r.city, r.district,
                r.state, r.ward, r.zone,
            )
            for r in records
        ]
        try:
            async with pool.acquire() as connection:
                await connection.executemany(sql, values)
        except Exception as exc:
            raise ProviderUnavailableError("complaint_database", str(exc)) from exc
        return len(records)

    async def list_complaints(self, query: ComplaintQuery) -> list[ComplaintObservation]:
        conditions = []
        args = []

        def add(value, expression):
            args.append(value)
            conditions.append(expression.format(index=len(args)))

        if query.start_at is not None:
            add(query.start_at, "reported_at >= ${index}")
        if query.end_at is not None:
            add(query.end_at, "reported_at <= ${index}")
        if query.issue_type:
            add(query.issue_type.casefold(), "lower(issue_type) = ${index}")
        if query.region:
            add(query.region.casefold(), "(")
            region_index = len(args)
            conditions[-1] = (
                f"(lower(coalesce(city, '')) = ${region_index} "
                f"OR lower(coalesce(district, '')) = ${region_index} "
                f"OR lower(coalesce(ward, '')) = ${region_index} "
                f"OR lower(coalesce(zone, '')) = ${region_index})"
            )
        if query.radius_meters is not None:
            if query.latitude is None or query.longitude is None:
                raise ValueError("latitude and longitude are required for a radius query")
            args.extend([query.longitude, query.latitude, query.radius_meters])
            point_index = len(args) - 2
            conditions.append(
                "ST_DWithin(location::geography, "
                f"ST_SetSRID(ST_MakePoint(${point_index}, ${point_index + 1}), 4326)::geography, "
                f"${point_index + 2})"
            )

        where_clause = " AND ".join(conditions) if conditions else "TRUE"
        sql = f"""
            SELECT complaint_id, issue_type, reported_at, latitude, longitude,
                   severity, description, image_ref, city, district, state, ward, zone
            FROM civic_complaint_index
            WHERE {where_clause}
            ORDER BY reported_at DESC
            LIMIT 5000
        """
        try:
            pool = await self._get_pool()
            rows = await pool.fetch(sql, *args)
        except Exception as exc:
            if isinstance(exc, ProviderUnavailableError):
                raise
            raise ProviderUnavailableError("complaint_database", str(exc)) from exc
        return [ComplaintObservation.model_validate(dict(row)) for row in rows]

    async def close(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            self._pool = None
