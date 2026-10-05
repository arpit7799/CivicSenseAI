# =============================================================================
# CivicSense AI — Authority Contracts
# =============================================================================
# Pydantic schemas for authority routing results.
# Owner: Arnav Yadav (Person 2)
# Interface defined by Arpit for cross-team integration.
#
# CRITICAL: Authority contact information MUST come from verified civic
# datasets — never from LLM generation. The 'source' and 'verified_at'
# fields exist to enforce this provenance requirement.
# =============================================================================

from pydantic import BaseModel, Field


class AuthorityResult(BaseModel):
    """
    Authority routing result — maps issue type + jurisdiction to the
    responsible civic authority and department.

    Implementation owner: Arnav (Person 2).
    Arpit's LLM consumes this verified data but MUST NOT generate it.
    """

    authority_name: str = Field(..., description="Name of the responsible authority")
    department: str = Field(..., description="Responsible department within the authority")
    jurisdiction: str = Field(..., description="Jurisdiction area (city, district, etc.)")
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
        description="Data source: 'mock' | 'verified_dataset' | 'civic_authority_db'",
    )
    verified_at: str | None = Field(
        default=None,
        description="ISO timestamp of last verification of this authority record",
    )
