# =============================================================================
# CivicSense AI — Embeddings Engine (BGE)
# =============================================================================
# Computes dense vector embeddings using BAAI/bge-small-en-v1.5.
#
# Provides an abstract base class `EmbeddingModel` to allow deterministic,
# zero-network unit tests using MockEmbeddingModel.
#
# Owner: Arpit (Person 1)
# =============================================================================

from abc import ABC, abstractmethod
from typing import Sequence
import numpy as np

from app.core.logging import get_logger
from app.core.errors import ModelNotLoadedError

logger = get_logger(__name__)


class EmbeddingModel(ABC):
    """Abstract interface for embedding generation."""

    @abstractmethod
    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        """Generate dense embeddings for a sequence of texts."""
        ...

    @abstractmethod
    def embed_query(self, query: str) -> list[float]:
        """Generate a dense embedding for a search query."""
        ...

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return the vector dimensionality."""
        ...


class MockEmbeddingModel(EmbeddingModel):
    """
    Deterministic embedding model for isolated unit tests.
    Does NOT require network access or downloading external model weights.
    Generates repeatable pseudo-embeddings derived from text length & character hash.
    """

    def __init__(self, dimension: int = 384):
        self._dim = dimension

    @property
    def dimension(self) -> int:
        return self._dim

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        return [self._embed_single(t) for t in texts]

    def embed_query(self, query: str) -> list[float]:
        return self._embed_single(query)

    def _embed_single(self, text: str) -> list[float]:
        vec = np.zeros(self._dim, dtype=np.float32)
        words = text.lower().split()
        for idx, word in enumerate(words):
            val = (sum(ord(c) for c in word) % 100) / 100.0
            pos = (idx * 17) % self._dim
            vec[pos] += val
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        else:
            vec[0] = 1.0
        return vec.tolist()


class BGEEmbeddingModel(EmbeddingModel):
    """
    Production embedding engine using sentence-transformers (BAAI/bge-small-en-v1.5).
    """

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model_name = model_name
        self._model = None
        self._dim = 384

    def _load(self):
        if self._model is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
            self._dim = self._model.get_sentence_embedding_dimension()
        except Exception as exc:
            logger.error(f"Failed to load embedding model '{self.model_name}': {exc}")
            raise ModelNotLoadedError(self.model_name) from exc

    @property
    def dimension(self) -> int:
        if self._model is None:
            return self._dim
        return self._model.get_sentence_embedding_dimension()

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        self._load()
        embeddings = self._model.encode(
            list(texts),
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return embeddings.tolist()

    def embed_query(self, query: str) -> list[float]:
        self._load()
        # BGE models benefit from instruction prefix for retrieval queries
        formatted = f"Represent this sentence for searching relevant passages: {query}"
        embedding = self._model.encode(
            formatted,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return embedding.tolist()
