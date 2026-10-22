# =============================================================================
# CivicSense AI — YOLO Detector Tests
# =============================================================================

import pytest
from unittest.mock import patch, MagicMock
import numpy as np

from app.vision.detector import YOLODetector
from app.contracts.vision import VisionResult

@pytest.fixture
def mock_ultralytics_results():
    """Mock the Ultralytics Results object."""
    mock_box1 = MagicMock()
    mock_box1.conf = [0.95]
    mock_box1.cls = [0]
    mock_box1.xyxy = [[10.0, 20.0, 100.0, 200.0]]
    
    mock_box2 = MagicMock()
    mock_box2.conf = [0.80]
    mock_box2.cls = [1]
    mock_box2.xyxy = [[50.0, 60.0, 150.0, 250.0]]

    mock_boxes = [mock_box1, mock_box2]

    # Create an iterable boxes object that behaves like ultralytics.engine.results.Boxes
    mock_boxes_obj = MagicMock()
    mock_boxes_obj.__len__.return_value = len(mock_boxes)
    mock_boxes_obj.__getitem__.side_effect = lambda idx: mock_boxes[idx]
    
    # We need to simulate truthiness for if result.boxes:
    mock_boxes_obj.__bool__.return_value = True

    mock_result = MagicMock()
    mock_result.boxes = mock_boxes_obj
    
    return [mock_result]

@patch('app.vision.detector.YOLO')
@patch('app.vision.detector.assess_and_decode_image')
@patch('app.vision.detector.download_image')
@pytest.mark.anyio
async def test_yolo_detector_inference(
    mock_download, mock_assess, mock_yolo_class, mock_ultralytics_results
):
    # Setup mocks
    mock_download.return_value = b"fake_image_bytes"
    from app.contracts.vision import ImageQuality
    mock_quality = ImageQuality(
        is_valid=True,
        resolution_adequate=True,
        blur_score=0.1,
        overall_quality_score=0.9,
        issues=[]
    )
    mock_assess.return_value = (np.zeros((100, 100, 3)), mock_quality)
    
    mock_yolo_instance = MagicMock()
    mock_yolo_instance.predict.return_value = mock_ultralytics_results
    mock_yolo_instance.names = {0: "pothole", 1: "road_damage"}
    mock_yolo_class.return_value = mock_yolo_instance

    # Run
    detector = YOLODetector(model_path="dummy.pt")
    result = await detector.detect("http://example.com/test.jpg")
    
    # Verify
    assert isinstance(result, VisionResult)
    assert len(result.detections) == 2
    assert result.primary_issue.issue_class == "pothole"
    assert result.primary_issue.confidence == 0.95
    assert result.secondary_issues[0].issue_class == "road_damage"
    assert result.secondary_issues[0].confidence == 0.80
    assert result.source == "yolov8"
    assert result.primary_issue.bounding_box.x_min == 10.0
