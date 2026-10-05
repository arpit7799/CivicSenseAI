# =============================================================================
# CivicSense AI — Mock Authority Provider
# =============================================================================
# ⚠️  MOCK IMPLEMENTATION — NOT PRODUCTION CIVIC INTELLIGENCE
#
# This mock returns placeholder authority data for development/testing.
# To be replaced by Arnav Yadav (Person 2) with real authority routing
# using verified civic datasets.
#
# CRITICAL: Authority contact information MUST come from verified civic
# datasets in production — never from LLM generation.
#
# Owner of interface: Shared
# Owner of real implementation: Arnav Yadav (Person 2)
# =============================================================================

_MOCK_WARNING = "⚠️ THIS IS A MOCK IMPLEMENTATION — NOT PRODUCTION CIVIC INTELLIGENCE"

from app.core.interfaces import AuthorityProvider
from app.contracts.location import LocationResult
from app.contracts.authority import AuthorityResult
from app.core.logging import get_logger

logger = get_logger(__name__)


class MockAuthorityProvider(AuthorityProvider):
    """
    MOCK: Returns placeholder authority routing data.

    Replace with Arnav's real AuthorityProvider implementation
    (civic authority dataset, jurisdiction mapping, department routing).

    All outputs are clearly marked with source='mock' and
    verified_at=None to indicate this is NOT verified data.
    """

    async def route(
        self, issue_type: str, location: LocationResult
    ) -> AuthorityResult:
        logger.info(
            f"[MOCK] Authority routing for issue_type='{issue_type}' "
            f"in city='{location.city}'"
        )

        return AuthorityResult(
            authority_name="Mock Municipal Corporation (Replace with Arnav's implementation)",
            department="Mock Public Works Department",
            jurisdiction=f"Mock Jurisdiction — {location.city}",
            contact_email=None,  # Explicitly None — mock does NOT fabricate contacts
            contact_phone=None,  # Explicitly None — mock does NOT fabricate contacts
            office_address=None,
            confidence=0.0,
            source="mock",
            verified_at=None,  # Not verified — this is a mock
        )
