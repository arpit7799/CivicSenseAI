"""Non-persistent read-model adapter for local development and tests."""

from app.contracts.civic_record import ComplaintObservation
from app.core.complaint_repository import ComplaintQuery
from app.duplicate.engine import haversine_meters


class InMemoryComplaintRepository:
    def __init__(self):
        self._records: dict[str, ComplaintObservation] = {}

    async def upsert_observations(self, records: list[ComplaintObservation]) -> int:
        for record in records:
            self._records[record.complaint_id] = record
        return len(records)

    async def list_complaints(self, query: ComplaintQuery) -> list[ComplaintObservation]:
        records = list(self._records.values())
        if query.start_at is not None:
            records = [record for record in records if record.reported_at >= query.start_at]
        if query.end_at is not None:
            records = [record for record in records if record.reported_at <= query.end_at]
        if query.issue_type:
            issue = query.issue_type.casefold()
            records = [record for record in records if record.issue_type.casefold() == issue]
        if query.region:
            region = query.region.casefold()
            records = [
                record
                for record in records
                if region in {
                    value.casefold()
                    for value in (record.city, record.district, record.ward, record.zone)
                    if value
                }
            ]
        if query.radius_meters is not None:
            if query.latitude is None or query.longitude is None:
                raise ValueError("latitude and longitude are required for a radius query")
            records = [
                record
                for record in records
                if haversine_meters(
                    query.latitude,
                    query.longitude,
                    record.latitude,
                    record.longitude,
                ) <= query.radius_meters
            ]
        return records
