# =============================================================================
# CivicSense AI — Error Handling
# =============================================================================
# Defines project-wide exceptions and FastAPI exception handlers.
# All errors return structured JSON responses.
# =============================================================================

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.logging import get_logger

logger = get_logger(__name__)


# =============================================================================
# Base Exception
# =============================================================================

class CivicSenseError(Exception):
    """Base exception for all CivicSense AI errors."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR", details: dict | None = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


# =============================================================================
# Image / Vision Errors
# =============================================================================

class ImageValidationError(CivicSenseError):
    """Raised when an image fails validation (format, resolution, blur, corruption)."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message=message, code="IMAGE_VALIDATION_ERROR", details=details)


class ModelNotLoadedError(CivicSenseError):
    """Raised when a required ML model is not loaded or unavailable."""

    def __init__(self, model_name: str):
        super().__init__(
            message=f"Model '{model_name}' is not loaded or unavailable",
            code="MODEL_NOT_LOADED",
            details={"model_name": model_name},
        )


# =============================================================================
# Provider Errors
# =============================================================================

class ProviderUnavailableError(CivicSenseError):
    """Raised when a service provider (location, authority, etc.) is unavailable."""

    def __init__(self, provider_name: str, reason: str = ""):
        super().__init__(
            message=f"Provider '{provider_name}' is unavailable: {reason}",
            code="PROVIDER_UNAVAILABLE",
            details={"provider_name": provider_name, "reason": reason},
        )


# =============================================================================
# AI Pipeline Errors
# =============================================================================

class AIServiceError(CivicSenseError):
    """Raised for generic AI service failures."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message=message, code="AI_SERVICE_ERROR", details=details)


class SeverityAssessmentError(CivicSenseError):
    """Raised when severity assessment fails."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message=message, code="SEVERITY_ASSESSMENT_ERROR", details=details)


class RAGRetrievalError(CivicSenseError):
    """Raised when RAG retrieval fails."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message=message, code="RAG_RETRIEVAL_ERROR", details=details)


class LLMGenerationError(CivicSenseError):
    """Raised when LLM complaint generation fails."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message=message, code="LLM_GENERATION_ERROR", details=details)


class ComplaintGenerationError(CivicSenseError):
    """Raised when structured complaint generation fails."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message=message, code="COMPLAINT_GENERATION_ERROR", details=details)


# =============================================================================
# FastAPI Exception Handlers
# =============================================================================

def register_exception_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers with the FastAPI app."""

    @app.exception_handler(CivicSenseError)
    async def civicsense_error_handler(request: Request, exc: CivicSenseError) -> JSONResponse:
        """Handle all CivicSense-specific errors."""
        logger.error(
            f"CivicSenseError [{exc.code}]: {exc.message}",
            extra={"details": exc.details},
        )
        status_code = _get_status_code(exc)
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Catch-all for unhandled exceptions — never leak stack traces."""
        logger.exception(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "details": {},
                }
            },
        )


def _get_status_code(exc: CivicSenseError) -> int:
    """Map exception types to HTTP status codes."""
    status_map = {
        ImageValidationError: 400,
        ModelNotLoadedError: 503,
        ProviderUnavailableError: 503,
        SeverityAssessmentError: 500,
        RAGRetrievalError: 500,
        LLMGenerationError: 500,
        ComplaintGenerationError: 500,
        AIServiceError: 500,
    }
    return status_map.get(type(exc), 500)
