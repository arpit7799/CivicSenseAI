# =============================================================================
# CivicSense AI — Severity Engine Tests
# =============================================================================

import pytest
from app.severity.engine import SeverityEngine
from app.contracts.vision import VisionResult, Detection, BoundingBox, ImageQuality

@pytest.fixture
def severity_engine():
    return SeverityEngine()

def create_mock_vision_result(primary_class="pothole", secondary_classes=None, area=1000):
    secondary_issues = []
    if secondary_classes:
        for cls in secondary_classes:
            secondary_issues.append(Detection(
                issue_class=cls,
                confidence=0.8,
                bounding_box=BoundingBox(x_min=0, y_min=0, x_max=10, y_max=10)
            ))
            
    import math
    side = math.sqrt(area)
    
    return VisionResult(
        detections=[],
        primary_issue=Detection(
            issue_class=primary_class,
            confidence=0.9,
            bounding_box=BoundingBox(x_min=0, y_min=0, x_max=side, y_max=side)
        ),
        secondary_issues=secondary_issues,
        image_quality=ImageQuality(is_valid=True, resolution_adequate=True, blur_score=0.1, overall_quality_score=0.9, issues=[]),
        classification_status="valid_civic_issue",
        processing_time_ms=10.0,
        model_version="test-1",
        source="test"
    )

@pytest.mark.anyio
async def test_severity_base_score(severity_engine):
    """Test that a basic issue gets its defined base score and correct level."""
    # Base score for broken_streetlight is 0.30 (LOW)
    vr = create_mock_vision_result(primary_class="broken_streetlight", area=1000)
    result = await severity_engine.assess(vr)
    
    assert result.score == 0.30
    assert result.level == "LOW"
    assert "base_issue_type:broken_streetlight" in result.factors

@pytest.mark.anyio
async def test_severity_compounding_rules(severity_engine):
    """Test that actual math compounding rules work correctly, rather than forcing a CRITICAL label."""
    # Base for pothole = 0.50
    # Modifier for water_logging = 0.20
    # Heuristic area (1000) = 0.0
    # Expected total = 0.70 (HIGH)
    vr = create_mock_vision_result(primary_class="pothole", secondary_classes=["water_logging"], area=1000)
    result = await severity_engine.assess(vr)
    
    assert result.score == 0.70
    assert result.level == "HIGH"
    assert "compounding_issue:water_logging" in result.factors

@pytest.mark.anyio
async def test_severity_large_area_heuristic(severity_engine):
    """Test that a large bounding box area bumps the score slightly as a heuristic."""
    # Base for fallen_tree = 0.70
    # Area > 50000 -> +0.10
    # Expected total = 0.80 (HIGH)
    vr = create_mock_vision_result(primary_class="fallen_tree", area=60000)
    result = await severity_engine.assess(vr)
    
    assert result.score == 0.80
    assert "heuristic_large_apparent_size" in result.factors

@pytest.mark.anyio
async def test_severity_clamps_to_max(severity_engine):
    """Test that a bunch of modifiers can't push the score past 1.0 (CRITICAL)."""
    # fallen_tree = 0.70
    # area > 50000 = +0.10
    # road_damage = +0.15
    # pothole = +0.15
    # Total would be 1.10 -> clamped to 1.0
    vr = create_mock_vision_result(
        primary_class="fallen_tree", 
        secondary_classes=["road_damage", "pothole"], 
        area=60000
    )
    result = await severity_engine.assess(vr)
    
    assert result.score == 1.0
    assert result.level == "CRITICAL"
