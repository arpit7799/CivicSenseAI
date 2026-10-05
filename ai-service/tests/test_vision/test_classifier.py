# =============================================================================
# CivicSense AI — Classifier Tests
# =============================================================================

from app.vision.classifier import classify_detections
from app.contracts.vision import Detection, BoundingBox

def test_classify_valid_civic_issues():
    # Mix of valid civic issues and invalid generic objects (cat)
    d1 = Detection(
        issue_class="pothole",
        confidence=0.95,
        bounding_box=BoundingBox(x_min=0, y_min=0, x_max=10, y_max=10)
    )
    d2 = Detection(
        issue_class="cat",
        confidence=0.99, # High confidence, but invalid class
        bounding_box=BoundingBox(x_min=0, y_min=0, x_max=10, y_max=10)
    )
    d3 = Detection(
        issue_class="road_damage",
        confidence=0.85,
        bounding_box=BoundingBox(x_min=0, y_min=0, x_max=10, y_max=10)
    )
    d4 = Detection(
        issue_class="pothole",
        confidence=0.40, # Below 0.50 threshold
        bounding_box=BoundingBox(x_min=0, y_min=0, x_max=10, y_max=10)
    )
    
    primary, secondary, status = classify_detections([d1, d2, d3, d4])
    
    assert status == "valid_civic_issue"
    assert primary.issue_class == "pothole"
    assert primary.confidence == 0.95
    assert len(secondary) == 1
    assert secondary[0].issue_class == "road_damage"
    # The cat and low-confidence pothole should be filtered out

def test_classify_only_non_civic_issues():
    d1 = Detection(
        issue_class="cat",
        confidence=0.95,
        bounding_box=BoundingBox(x_min=0, y_min=0, x_max=10, y_max=10)
    )
    
    primary, secondary, status = classify_detections([d1])
    
    assert primary is None
    assert len(secondary) == 0
    assert status == "no_civic_issue_detected"
