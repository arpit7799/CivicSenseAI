# =============================================================================
# CivicSense AI — Qdrant RAG Retriever
# =============================================================================
# Implements the RAGProvider interface using Qdrant vector database and
# dense vector embeddings (BGE).
#
# Supports:
# - In-memory Qdrant client (for local execution, tests, and zero-infra mode)
# - Remote Qdrant server connection (for production deployment)
# - Metadata filtering and cosine similarity score thresholding
# - Clean error degradation consistent with Phase 5 architecture
#
# Owner: Arpit (Person 1)
# =============================================================================

from typing import Sequence
import uuid

from app.core.interfaces import RAGProvider
from app.core.logging import get_logger
from app.core.errors import RAGRetrievalError
from app.config import get_settings
from app.rag.embeddings import EmbeddingModel, BGEEmbeddingModel
from app.rag.ingestion import CivicDocument, DocumentChunk, chunk_document
from app.rag.seed_corpus import SEED_CIVIC_DOCUMENTS

logger = get_logger(__name__)


class QdrantRAGRetriever(RAGProvider):
    """
    RAG retriever backed by Qdrant vector store and BGE embeddings.
    """

    def __init__(
        self,
        embedding_model: EmbeddingModel | None = None,
        in_memory: bool | None = None,
        collection_name: str | None = None,
        similarity_threshold: float | None = None,
        top_k: int | None = None,
    ):
        settings = get_settings()
        self.in_memory = in_memory if in_memory is not None else settings.qdrant_in_memory
        self.collection_name = collection_name or settings.qdrant_collection
        self.similarity_threshold = (
            similarity_threshold if similarity_threshold is not None else settings.rag_similarity_threshold
        )
        self.top_k = top_k if top_k is not None else settings.rag_top_k
        self._embedding_model = embedding_model or BGEEmbeddingModel(model_name=settings.bge_model_name)
        self._client = None
        self._initialized = False

    def _init_client(self):
        """Initialize Qdrant client and ensure collection exists."""
        if self._initialized and self._client is not None:
            return

        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams

            settings = get_settings()
            if self.in_memory:
                logger.info("Initializing in-memory Qdrant client")
                self._client = QdrantClient(location=":memory:")
            else:
                logger.info(f"Connecting to Qdrant at {settings.qdrant_host}:{settings.qdrant_port}")
                self._client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)

            dim = self._embedding_model.dimension
            # Check existing collections
            collections = [c.name for c in self._client.get_collections().collections]
            if self.collection_name not in collections:
                logger.info(f"Creating Qdrant collection: {self.collection_name} (dim={dim})")
                self._client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
                )
                # Seed collection with standard civic documents
                self.index_documents(SEED_CIVIC_DOCUMENTS)

            self._initialized = True
        except Exception as exc:
            logger.error(f"Failed to initialize Qdrant vector store: {exc}")
            raise RAGRetrievalError(f"Vector database initialization failed: {exc}") from exc

    def index_documents(self, documents: Sequence[CivicDocument]) -> int:
        """
        Chunk, embed, and index a collection of civic documents into Qdrant.
        Returns the number of indexed chunks.
        """
        if self._client is None:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams
            self._client = QdrantClient(location=":memory:")
            self._client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self._embedding_model.dimension, distance=Distance.COSINE),
            )
            self._initialized = True

        all_chunks: list[DocumentChunk] = []
        for doc in documents:
            all_chunks.extend(chunk_document(doc))

        if not all_chunks:
            return 0

        texts = [c.text for c in all_chunks]
        vectors = self._embedding_model.embed_texts(texts)

        from qdrant_client.models import PointStruct

        points = []
        for idx, (chunk, vec) in enumerate(zip(all_chunks, vectors)):
            payload = {
                "chunk_id": chunk.chunk_id,
                "document_id": chunk.document_id,
                "text": chunk.text,
                "category": chunk.category,
                "source_authority": chunk.source_authority,
                "source_title": chunk.source_title,
                "verification_status": chunk.verification_status,
                "department": chunk.department,
                "jurisdiction": chunk.jurisdiction,
                **chunk.metadata,
            }
            # Deterministic integer/UUID ID for Qdrant point
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk.chunk_id))
            points.append(PointStruct(id=point_id, vector=vec, payload=payload))

        self._client.upsert(collection_name=self.collection_name, points=points)
        logger.info(f"Indexed {len(points)} civic chunks into Qdrant collection '{self.collection_name}'")
        return len(points)

    async def retrieve(self, query: str, context: dict | None = None) -> dict:
        """
        Retrieve top-k relevant civic documents matching the query.
        Applies cosine similarity score thresholding.
        """
        try:
            self._init_client()
        except Exception as exc:
            logger.warning(f"Qdrant RAG retriever unavailable: {exc}")
            raise RAGRetrievalError(str(exc)) from exc

        logger.info(f"Executing RAG semantic search for: '{query[:80]}' (threshold={self.similarity_threshold})")

        try:
            query_vector = self._embedding_model.embed_query(query)
            
            # Execute vector search
            # Compatibility with both search() and query_points() in qdrant-client
            if hasattr(self._client, "search"):
                search_results = self._client.search(
                    collection_name=self.collection_name,
                    query_vector=query_vector,
                    limit=self.top_k,
                )
            else:
                res = self._client.query_points(
                    collection_name=self.collection_name,
                    query=query_vector,
                    limit=self.top_k,
                )
                search_results = res.points

            matched_docs: list[str] = []
            scores: list[float] = []
            structured_records: list[dict] = []

            for hit in search_results:
                score = float(hit.score)
                # Cosine similarity filtering: discard low confidence matches
                if score < self.similarity_threshold:
                    continue

                payload = hit.payload or {}
                text = payload.get("text", "")
                auth = payload.get("source_authority", "Unknown Authority")
                title = payload.get("source_title", "Civic Record")
                v_status = payload.get("verification_status", "general_guidance")

                # Format chunk with unambiguous provenance indicator
                formatted_doc = (
                    f"[{v_status.upper()}] {auth} — '{title}':\n{text}"
                )
                matched_docs.append(formatted_doc)
                scores.append(round(score, 4))
                structured_records.append({
                    "text": text,
                    "score": round(score, 4),
                    "source_authority": auth,
                    "source_title": title,
                    "verification_status": v_status,
                    "category": payload.get("category", "general"),
                })

            return {
                "documents": matched_docs,
                "scores": scores,
                "records": structured_records,
                "total_retrieved": len(matched_docs),
                "source": "qdrant_bge",
            }
        except Exception as exc:
            logger.error(f"Semantic search query failed: {exc}")
            raise RAGRetrievalError(f"RAG query error: {exc}") from exc
