# =============================================================================
# CivicSense AI — Mock Complaint Generator
# =============================================================================
# Offline / development complaint generator.
# Uses deterministic template generation to construct formal civic complaints.
# Outputs source='mock'.
# =============================================================================

from app.core.interfaces import ComplaintGenerator
from app.contracts.complaint import ComplaintResult
from app.llm.fallback import generate_deterministic_complaint
from app.core.logging import get_logger

logger = get_logger(__name__)


class MockComplaintGenerator(ComplaintGenerator):
    """
    Constructs formal civic complaints deterministically from decision context.
    Provides complete, professional grievance letters without external LLM dependencies.
    Outputs source='mock'.
    """

    async def generate(self, decision_context: dict) -> ComplaintResult:
        logger.info("[MOCK] Generating deterministic civic complaint")

        # Use robust deterministic complaint generator
        complaint = generate_deterministic_complaint(decision_context)
        return complaint.model_copy(update={"source": "mock"})

