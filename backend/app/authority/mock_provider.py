# =============================================================================
# CivicSense AI — Mock Authority Provider
# =============================================================================
# Lightweight offline authority routing provider for development and testing.
# Maps civic issue types and municipal jurisdictions to realistic authority records.
# =============================================================================

from app.core.interfaces import AuthorityProvider
from app.contracts.location import LocationResult
from app.contracts.authority import AuthorityResult
from app.core.logging import get_logger

logger = get_logger(__name__)

DEPARTMENT_MAP = {
    "pothole": "Roads & Civil Works Division",
    "road_damage": "Roads & Civil Works Division",
    "garbage_dump": "Sanitation & Solid Waste Management Department",
    "broken_streetlight": "Electrical & Public Lighting Division",
    "water_logging": "Drainage & Sewerage Maintenance Division",
    "fallen_tree": "Horticulture & Urban Forestry Department",
}


class MockAuthorityProvider(AuthorityProvider):
    """
    Lightweight fallback/offline authority provider.
    Routes complaints to verified municipal departments for development.
    Outputs source='mock'.
    """

    async def route(
        self, issue_type: str, location: LocationResult
    ) -> AuthorityResult:
        logger.info(
            f"[MOCK] Authority routing for issue_type='{issue_type}' "
            f"in city='{location.city}'"
        )

        dept = DEPARTMENT_MAP.get(
            issue_type.strip().lower(),
            "Civil Engineering & Public Works Department"
        )
        city_name = location.city or "Gurugram"

        ward_str = location.ward if location.ward else "General Area"
        return AuthorityResult(
            authority_name=f"Municipal Corporation of {city_name}",
            department=dept,
            jurisdiction=f"{city_name} Municipal Corporation ({ward_str})",
            contact_email=None,
            contact_phone=None,
            office_address=None,
            confidence=0.85,
            source="mock",
            source_reference=None,
            verified_at=None,
        )

