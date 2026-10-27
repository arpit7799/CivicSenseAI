# =============================================================================
# CivicSense AI — Mock RAG Retriever
# =============================================================================
# ⚠️  MOCK IMPLEMENTATION — NOT PRODUCTION CIVIC INTELLIGENCE
#
# This mock returns placeholder RAG retrieval results for development/testing.
# Will be replaced with real BGE + Qdrant retrieval in Phase 6.
#
# Owner: Arpit (Person 1)
# =============================================================================

_MOCK_WARNING = "⚠️ THIS IS A MOCK IMPLEMENTATION — NOT PRODUCTION CIVIC INTELLIGENCE"

from app.core.interfaces import RAGProvider
from app.core.logging import get_logger

logger = get_logger(__name__)


class MockRAGRetriever(RAGProvider):
    """
    Lightweight fallback/offline RAG retrieval provider.
    Outputs source='mock'.
    """

    async def retrieve(self, query: str, context: dict | None = None) -> dict:
        logger.info(f"[MOCK] RAG retrieval for query: {query[:80]}...")

        return {
            "documents": [
                "MOCK DOCUMENT: Municipal Corporation is responsible for road maintenance "
                "including pothole repair. Citizens can file complaints through the "
                "official grievance portal.",
                "MOCK DOCUMENT: Road damage complaints should include photographic evidence "
                "and precise location. The Public Works Department handles road infrastructure.",
            ],
            "scores": [0.89, 0.76],
            "total_retrieved": 2,
            "source": "mock",
        }
