# =============================================================================
# CivicSense AI — AI Service Configuration
# =============================================================================
# All configuration is loaded from environment variables / .env file.
# Uses pydantic-settings for validation and type coercion.
# =============================================================================

from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ----- Application -----
    app_name: str = Field(default="CivicSense AI", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # ----- AI Service -----
    ai_service_host: str = Field(default="0.0.0.0", description="AI service bind host")
    ai_service_port: int = Field(default=8000, description="AI service bind port")
    api_v1_prefix: str = Field(default="/api/v1", description="API v1 route prefix")

    # ----- Vision Pipeline -----
    min_image_width: int = Field(default=64, description="Minimum allowed image width")
    min_image_height: int = Field(default=64, description="Minimum allowed image height")
    blur_variance_threshold: float = Field(default=50.0, description="Threshold for Variance of Laplacian (blur detection)")
    min_confidence_threshold: float = Field(default=0.50, description="Minimum YOLO confidence to accept a detection")
    civic_issue_classes: set[str] = Field(
        default={
            "pothole",
            "garbage_dump",
            "broken_streetlight",
            "road_damage",
            "water_logging",
            "fallen_tree"
        },
        description="Ontology of valid civic issue classes"
    )

    # ----- Model Paths -----
    model_dir: str = Field(default="./models", description="Directory for model weights")
    yolo_model_path: str = Field(
        default="./models/civicsense_yolo.pt",
        description="Path to YOLO model weights",
    )

    # ----- Qdrant (Phase 6) -----
    qdrant_host: str = Field(default="localhost", description="Qdrant server host")
    qdrant_port: int = Field(default=6333, description="Qdrant server port")
    qdrant_collection: str = Field(
        default="civicsense_docs", description="Qdrant collection name"
    )

    # ----- Ollama (Phase 7) -----
    ollama_host: str = Field(default="localhost", description="Ollama server host")
    ollama_port: int = Field(default=11434, description="Ollama server port")
    ollama_model: str = Field(default="llama3.2", description="Ollama model name")

    # ----- BGE Embeddings (Phase 6) -----
    bge_model_name: str = Field(
        default="BAAI/bge-small-en-v1.5", description="BGE embedding model name"
    )

    # ----- Redis (Future) -----
    redis_url: str = Field(
        default="redis://localhost:6379/0", description="Redis connection URL"
    )

    # ----- PostgreSQL (Future) -----
    database_url: str = Field(
        default="postgresql://user:password@localhost:5432/civicsense",
        description="PostgreSQL connection URL",
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }

    @property
    def model_dir_path(self) -> Path:
        """Return model directory as a Path object."""
        return Path(self.model_dir)

    @property
    def ollama_base_url(self) -> str:
        """Return Ollama API base URL."""
        return f"http://{self.ollama_host}:{self.ollama_port}"

    @property
    def qdrant_url(self) -> str:
        """Return Qdrant connection URL."""
        return f"http://{self.qdrant_host}:{self.qdrant_port}"


@lru_cache()
def get_settings() -> Settings:
    """
    Return cached application settings.

    Uses lru_cache to ensure settings are loaded once and reused.
    """
    return Settings()
