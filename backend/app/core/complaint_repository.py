"""Complaint read-model query boundary for Person 2 civic intelligence."""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from app.contracts.civic_record import ComplaintObservation


@dataclass(frozen=True)
class ComplaintQuery:
    start_at: datetime | None = None
    end_at: datetime | None = None
    issue_type: str | None = None
    region: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    radius_meters: float | None = None


class ComplaintRepository(Protocol):
    """Storage adapter expected to query the API-fed read projection."""

    async def list_complaints(self, query: ComplaintQuery) -> list[ComplaintObservation]:
        """Return observations matching the provided time, region, and radius filters."""
        ...

    async def upsert_observations(self, records: list[ComplaintObservation]) -> int:
        """Idempotently add or refresh complaint projection records."""
        ...
