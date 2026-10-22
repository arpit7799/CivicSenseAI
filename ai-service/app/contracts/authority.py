# =============================================================================
# CivicSense AI — Authority Contracts
# =============================================================================
# Pydantic schemas for authority routing results.
# Owner: Arnav Yadav (Person 2)
# Interface defined by Arpit for cross-team integration.
#
# CRITICAL: Authority contact information MUST come from verified civic
# datasets — never from LLM generation. Source, source reference, and
# verification timestamp are required whenever contact fields are present.
# =============================================================================

from pydantic import BaseModel, Field, model_validator

from app.contracts.location import LocationResult


class AuthorityRouteRequest(BaseModel):
    """Request payload for routing an issue to the responsible civic authority."""

    issue_type: str = Field(..., min_length=1, description="Civic issue classification")
    location: LocationResult = Field(..., description="Resolved geographic location context")


class AuthorityResult(BaseModel):
    """
    Authority routing result — maps issue type + jurisdiction to the
    responsible civic authority and department.

    Implementation owner: Arnav (Person 2).
    Arpit's LLM consumes this verified data but MUST NOT generate it.
    """

    authority_name: str | None = Field(default=None, description="Name of the responsible authority, if resolved")
    department: str | None = Field(default=None, description="Responsible department, if resolved")
    jurisdiction: str | None = Field(default=None, description="Matched jurisdiction, if resolved")
    contact_email: str | None = Field(
        default=None,
        description="Official contact email (from verified dataset only)",
    )
    contact_phone: str | None = Field(
        default=None,
        description="Official contact phone (from verified dataset only)",
    )
    office_address: str | None = Field(
        default=None,
        description="Office address (from verified dataset only)",
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0,
        description="Confidence in the authority routing",
    )
    source: str = Field(
        default="mock",
        description="Data source: 'mock' | 'no_match' | 'verified_dataset' | 'civic_authority_db'",
    )
    source_reference: str | None = Field(
        default=None,
        description="Official source URL or document identifier for this authority record",
    )
    verified_at: str | None = Field(
        default=None,
        description="ISO timestamp of last verification of this authority record",
    )

    @model_validator(mode="after")
    def contacts_must_be_verified(self) -> "AuthorityResult":
        """Prevent unverified authority contacts from reaching complaint generation."""
        has_contact = any(
            (self.contact_email, self.contact_phone, self.office_address)
        )
        trusted_sources = {"verified_dataset", "civic_authority_db"}
        if has_contact and (
            self.source not in trusted_sources
            or self.verified_at is None
            or self.source_reference is None
        ):
            raise ValueError(
                "Authority contacts require a verified civic data source, source reference, and verification timestamp"
            )
        return self
