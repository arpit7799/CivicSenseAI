# =============================================================================
# CivicSense AI — Vision Contracts
# =============================================================================
# Pydantic schemas for computer vision detection results.
# Owner: Arpit (Person 1)
# =============================================================================

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Bounding box coordinates for a detected object."""

    x_min: float = Field(..., ge=0.0, description="Left edge (pixels or normalized)")
    y_min: float = Field(..., ge=0.0, description="Top edge (pixels or normalized)")
    x_max: float = Field(..., ge=0.0, description="Right edge (pixels or normalized)")
    y_max: float = Field(..., ge=0.0, description="Bottom edge (pixels or normalized)")


class Detection(BaseModel):
    """A single detected civic issue in an image."""

    issue_class: str = Field(..., description="Detected issue class, e.g. 'pothole'")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence 0–1")
    bounding_box: BoundingBox = Field(..., description="Object bounding box")


class ImageQuality(BaseModel):
    """Image quality assessment results."""

    is_valid: bool = Field(..., description="Whether the image passes quality checks")
    resolution_adequate: bool = Field(..., description="Whether resolution is sufficient")
    blur_score: float = Field(
        ..., ge=0.0, le=1.0,
        description="Blur score: 0.0 = sharp, 1.0 = very blurry",
    )
    overall_quality_score: float = Field(
        ..., ge=0.0, le=1.0,
        description="Overall quality score 0–1",
    )
    issues: list[str] = Field(
        default_factory=list,
        description="List of quality issues found, e.g. ['too_dark', 'too_blurry']",
    )


class VisionResult(BaseModel):
    """Complete vision pipeline output."""

    detections: list[Detection] = Field(
        default_factory=list, description="All detected civic issues"
    )
    primary_issue: Detection | None = Field(
        default=None, description="Highest-confidence detection selected as primary"
    )
    secondary_issues: list[Detection] = Field(
        default_factory=list, description="Other detected issues"
    )
    image_quality: ImageQuality = Field(..., description="Image quality assessment")
    classification_status: str = Field(
        default="valid_civic_issue", 
        description="Status of classification, e.g., 'valid_civic_issue', 'no_civic_issue_detected'"
    )
    processing_time_ms: float = Field(
        ..., ge=0.0, description="Vision pipeline processing time in milliseconds"
    )
    model_version: str = Field(
        default="mock-v0", description="Vision model version identifier"
    )
    source: str = Field(
        default="mock",
        description="Result source: 'mock' | 'yolo_v8' | etc.",
    )
