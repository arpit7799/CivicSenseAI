# =============================================================================
# CivicSense AI — RAG Vector Retrieval Unit Tests
# =============================================================================
# Deterministic, zero-network unit tests using MockEmbeddingModel and in-memory
# Qdrant vector storage. Does NOT require downloading model weights or external servers.
# =============================================================================

import pytest

from app.rag.embeddings import MockEmbeddingModel
from app.rag.retriever import QdrantRAGRetriever
from app.rag.ingestion import CivicDocument, DocumentSource, VerificationStatus
from app.core.errors import RAGRetrievalError


@pytest.fixture
def mock_embedding_model():
    return MockEmbeddingModel(dimension=64)


@pytest.fixture
def sample_civic_docs():
    return [
        CivicDocument(
            id="TEST-ROAD-01",
            category="roads",
            source=DocumentSource(
                authority_name="Municipal Road Works",
                title="Pothole Repair Manual",
                reference_id="MRW/2024/01",
                verification_status=VerificationStatus.VERIFIED_OFFICIAL,
            ),
            text="Pothole repairs on municipal asphalt roads must be executed promptly.",
        ),
        CivicDocument(
            id="TEST-WASTE-02",
            category="sanitation",
            source=DocumentSource(
                authority_name="Sanitation Board",
                title="Garbage Collection Standard",
                verification_status=VerificationStatus.VERIFIED_OFFICIAL,
            ),
            text="Garbage dumps and commercial waste overflow must be cleared daily.",
        ),
        CivicDocument(
            id="TEST-GUIDE-03",
            category="general",
            source=DocumentSource(
                authority_name="Community Volunteers",
                title="Citizen Reporting Suggestions",
                verification_status=VerificationStatus.GENERAL_GUIDANCE,
            ),
            text="General suggestions for citizens submitting neighborhood complaints.",
        ),
    ]


@pytest.mark.anyio
async def test_qdrant_retriever_indexes_and_retrieves_documents(mock_embedding_model, sample_civic_docs):
    """Retriever indexes documents into in-memory Qdrant and retrieves matches."""
    retriever = QdrantRAGRetriever(
        embedding_model=mock_embedding_model,
        in_memory=True,
        collection_name="test_civic_docs_unique",
        similarity_threshold=0.0,  # accept matches for test
        top_k=2,
    )
    indexed_count = retriever.index_documents(sample_civic_docs)
    assert indexed_count == 3

    result = await retriever.retrieve("pothole repair road")
    assert result["source"] == "qdrant_bge"
    assert len(result["documents"]) > 0
    assert result["total_retrieved"] == len(result["documents"])
    assert len(result["scores"]) == len(result["documents"])

    # Output document includes explicit source reliability tag
    first_doc = result["documents"][0]
    assert "[VERIFIED_OFFICIAL]" in first_doc or "[GENERAL_GUIDANCE]" in first_doc


@pytest.mark.anyio
async def test_qdrant_retriever_applies_similarity_threshold(mock_embedding_model, sample_civic_docs):
    """Retriever drops chunks that do not meet the similarity threshold."""
    retriever = QdrantRAGRetriever(
        embedding_model=mock_embedding_model,
        in_memory=True,
        collection_name="test_threshold_docs",
        similarity_threshold=0.9999,  # Unattainable threshold to test filtering
        top_k=5,
    )
    retriever.index_documents(sample_civic_docs)

    result = await retriever.retrieve("completely unrelated acoustic quantum astrophysics")
    # All hits dropped due to high similarity threshold
    assert result["documents"] == []
    assert result["scores"] == []
    assert result["total_retrieved"] == 0


@pytest.mark.anyio
async def test_qdrant_retriever_preserves_structured_provenance_records(mock_embedding_model, sample_civic_docs):
    """Retriever returns structured provenance records matching the input metadata."""
    retriever = QdrantRAGRetriever(
        embedding_model=mock_embedding_model,
        in_memory=True,
        collection_name="test_provenance_docs",
        similarity_threshold=0.0,
        top_k=1,
    )
    retriever.index_documents(sample_civic_docs)

    result = await retriever.retrieve("pothole asphalt")
    assert len(result["records"]) == 1
    record = result["records"][0]

    assert "text" in record
    assert "score" in record
    assert "source_authority" in record
    assert "source_title" in record
    assert "verification_status" in record
    assert record["verification_status"] in ("verified_official", "general_guidance")


@pytest.mark.anyio
async def test_qdrant_retriever_graceful_error_on_uninitialized_client():
    """Uninitialized or broken vector store client raises RAGRetrievalError cleanly."""
    class BrokenModel(MockEmbeddingModel):
        def embed_query(self, query: str):
            raise RuntimeError("Embedding computation fault")

    retriever = QdrantRAGRetriever(
        embedding_model=BrokenModel(dimension=32),
        in_memory=True,
        collection_name="test_broken_docs",
    )
    with pytest.raises(RAGRetrievalError):
        await retriever.retrieve("test query")
