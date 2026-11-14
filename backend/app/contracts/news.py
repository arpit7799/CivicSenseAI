# =============================================================================
# CivicSense AI — Civic News Contracts
# =============================================================================
# Pydantic schemas for real-time civic, municipal, and infrastructure news feeds.
# =============================================================================

from pydantic import BaseModel, Field


class CivicNewsArticle(BaseModel):
    """Structured representation of a real-time civic news item."""

    title: str = Field(..., description="Article headline")
    description: str | None = Field(default=None, description="Concise news summary")
    source_name: str = Field(default="Municipal Dispatch", description="News publisher name")
    url: str = Field(..., description="Direct link to full article")
    url_to_image: str | None = Field(default=None, description="Featured image URL")
    published_at: str = Field(..., description="ISO publication timestamp")
    category: str = Field(
        default="Civic Infrastructure",
        description="Assigned civic domain, e.g. Roads & Traffic, Sanitation & Waste, Municipal Policy",
    )
    city: str = Field(default="Gurugram", description="Primary municipality or region")


class CivicNewsResponse(BaseModel):
    """Response payload for civic news queries."""

    city: str = Field(..., description="Queried city or municipality")
    category: str = Field(..., description="Filter category applied")
    total_results: int = Field(..., description="Count of relevant articles returned")
    articles: list[CivicNewsArticle] = Field(
        default_factory=list, description="List of tuned civic news items"
    )
    cached: bool = Field(default=False, description="Whether response was served from cache")
    last_updated: str = Field(..., description="ISO timestamp of data retrieval")

