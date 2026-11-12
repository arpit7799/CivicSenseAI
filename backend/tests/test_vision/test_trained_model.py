# =============================================================================
# CivicSense AI — Tests for Fine-Tuned Civic YOLO Model
# =============================================================================

from pathlib import Path
import pytest
from app.vision.detector import YOLODetector
from app.contracts.vision import VisionResult

VALID_CIVIC_CLASSES = {
    # New 10 classes & aliases
    "damaged_road_issues",
    "pothole_issues",
    "illegal_parking_issues",
    "broken_road_sign_issues",
    "fallen_trees",
    "littering_garbage_on_public_places",
    "vandalism_issues",
    "dead_animal_pollution",
    "damaged_concrete_structures",
    "damaged_electric_wires_and_poles",
    # canonical aliases
    "pothole",
    "garbage_dump",
    "broken_streetlight",
    "road_damage",
    "water_logging",
    "fallen_tree",
    "illegal_parking",
    "broken_road_sign",
    "graffiti",
    "vandalism",
}


@pytest.mark.asyncio
async def test_trained_civicsense_yolo_model_inference():
    """Verify that the fine-tuned civicsense_yolo.pt loads and predicts on civic imagery."""
    model_path = Path(__file__).resolve().parents[2] / "models" / "civicsense_yolo.pt"
    val_dir = Path(__file__).resolve().parents[2] / "datasets" / "civic_dataset" / "images" / "valid"
    
    if not model_path.exists() or not val_dir.exists():
        pytest.skip("Trained civic model or val directory not present in environment")
        
    val_images = list(val_dir.glob("*.jpg"))
    if not val_images:
        pytest.skip("No validation images found in civic_dataset")

    test_img = val_images[0]
    detector = YOLODetector(model_path=str(model_path))
    result: VisionResult = await detector.detect(str(test_img))
    
    assert result.source == "yolov8"
    assert result.image_quality.is_valid is True
    assert result.classification_status in (
        "valid_civic_issue",
        "no_civic_issue_detected",
        "inconclusive",
        "partial_civic_context",
    )
    if result.primary_issue is not None:
        assert result.primary_issue.issue_class in VALID_CIVIC_CLASSES
