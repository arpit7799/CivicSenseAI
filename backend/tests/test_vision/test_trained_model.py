# =============================================================================
# CivicSense AI — Tests for Fine-Tuned Civic YOLO Model
# =============================================================================

from pathlib import Path
import pytest
from app.vision.detector import YOLODetector
from app.contracts.vision import VisionResult

@pytest.mark.asyncio
async def test_trained_civicsense_yolo_model_inference():
    """Verify that the fine-tuned civicsense_yolo.pt loads and predicts on civic imagery."""
    model_path = Path(__file__).resolve().parents[2] / "models" / "civicsense_yolo.pt"
    test_img = Path(__file__).resolve().parents[2] / "datasets" / "civic_dataset" / "images" / "val" / "civic_val_0000.jpg"
    
    if not model_path.exists() or not test_img.exists():
        pytest.skip("Trained civic model or val image not present in environment")
        
    detector = YOLODetector(model_path=str(model_path))
    result: VisionResult = await detector.detect(str(test_img))
    
    assert result.source == "yolov8"
    assert result.image_quality.is_valid is True
    assert result.classification_status == "valid_civic_issue"
    assert result.primary_issue is not None
    assert result.primary_issue.confidence >= 0.50
    assert result.primary_issue.issue_class in [
        "pothole",
        "garbage_dump",
        "broken_streetlight",
        "road_damage",
        "water_logging",
        "fallen_tree"
    ]
