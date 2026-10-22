"""Read-only complaint projection supplied by the main application."""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator


SeverityValue = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]


class ComplaintObservation(BaseModel):
    complaint_id: str = Field(..., min_length=1)
    issue_type: str = Field(..., min_length=1)
    reported_at: datetime
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    severity: SeverityValue | None = None
    description: str | None = None
    image_ref: str | None = None
    city: str | None = None
    district: str | None = None
    state: str | None = None
    ward: str | None = None
    zone: str | None = None

    @field_validator("complaint_id", "issue_type")
    @classmethod
    def required_text_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("value must not be blank")
        return value

    @field_validator("reported_at")
    @classmethod
    def timestamp_must_be_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("reported_at must include a timezone")
        return value.astimezone(timezone.utc)


class ComplaintIndexUpsertRequest(BaseModel):
    records: list[ComplaintObservation] = Field(..., min_length=1, max_length=500)


class ComplaintIndexUpsertResponse(BaseModel):
    upserted: int = Field(..., ge=0)
