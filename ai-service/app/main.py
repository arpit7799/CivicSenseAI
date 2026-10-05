# =============================================================================
# CivicSense AI — FastAPI Application Entry Point
# =============================================================================
# This is the main FastAPI application for the AI service.
# Run with: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# =============================================================================

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.core.logging import setup_logging, get_logger
from app.core.errors import register_exception_handlers
from app.api.v1.router import router as v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown events."""
    settings = get_settings()
    setup_logging()
    logger = get_logger("main")

    logger.info("=" * 60)
    logger.info(f"  {settings.app_name} v{settings.app_version}")
    logger.info(f"  Debug: {settings.debug}")
    logger.info(f"  Log Level: {settings.log_level}")
    logger.info(f"  API Prefix: {settings.api_v1_prefix}")
    logger.info("=" * 60)
    logger.info("All providers: MOCK (Phase 1 — Foundation)")
    logger.info("Service started successfully")

    yield  # Application runs here

    logger.info("Service shutting down")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description=(
            "AI-powered civic complaint detection, analysis, and generation service. "
            "Accepts photographs of civic issues with GPS coordinates and returns "
            "structured detection, severity assessment, authority routing, and "
            "generated complaints."
        ),
        version=settings.app_version,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Register custom exception handlers
    register_exception_handlers(app)

    # Register API v1 router
    app.include_router(v1_router, prefix=settings.api_v1_prefix)

    return app


# Application instance — used by uvicorn
app = create_app()
