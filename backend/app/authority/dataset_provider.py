"""Authority routing from a locally maintained, provenance-bearing dataset."""

import json
from datetime import date
from pathlib import Path

from pydantic import BaseModel, Field, ValidationError

from app.contracts.authority import AuthorityResult
from app.contracts.location import LocationResult
from app.core.interfaces import AuthorityProvider


DEFAULT_DATASET_PATH = Path(__file__).resolve().parents[2] / "datasets" / "authority_routes.json"


class AuthorityRouteRecord(BaseModel):
    record_id: str
    authority_name: str
    department: str | None = None
    jurisdiction: str
    city_aliases: list[str]
    state_aliases: list[str]
    issue_types: list[str]
    contact_email: str | None = None
    contact_phone: str | None = None
    office_address: str | None = None
    source: str = Field(pattern="^(verified_dataset|civic_authority_db)$")
    source_reference: str
    verified_at: date
    confidence: float = Field(ge=0.0, le=1.0)
    verification_note: str


class VerifiedDatasetAuthorityProvider(AuthorityProvider):
    """Route only to records with explicit jurisdiction and source metadata."""

    def __init__(self, dataset_path: str | Path = DEFAULT_DATASET_PATH):
        self.dataset_path = Path(dataset_path)
        try:
            payload = json.loads(self.dataset_path.read_text(encoding="utf-8"))
            records = payload["records"]
            if not isinstance(records, list):
                raise ValueError("'records' must be a list")
            self._records = [AuthorityRouteRecord.model_validate(record) for record in records]
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError, ValidationError) as exc:
            raise ValueError(f"Invalid authority dataset at {self.dataset_path}: {exc}") from exc

    async def route(self, issue_type: str, location: LocationResult) -> AuthorityResult:
        issue = issue_type.strip().casefold()
        city = (location.city or "").strip().casefold()
        state = (location.state or "").strip().casefold()

        for record in self._records:
            if issue not in self._normalized_set(record.issue_types):
                continue
            if city not in self._normalized_set(record.city_aliases):
                continue
            if state not in self._normalized_set(record.state_aliases):
                continue
            return AuthorityResult(
                authority_name=record.authority_name,
                department=record.department,
                jurisdiction=record.jurisdiction,
                contact_email=record.contact_email,
                contact_phone=record.contact_phone,
                office_address=record.office_address,
                confidence=record.confidence,
                source=record.source,
                source_reference=record.source_reference,
                verified_at=record.verified_at.isoformat(),
            )

        return AuthorityResult(
            confidence=0.0,
            source="no_match",
        )

    @staticmethod
    def _normalized_set(values: list[str]) -> set[str]:
        return {value.strip().casefold() for value in values}
