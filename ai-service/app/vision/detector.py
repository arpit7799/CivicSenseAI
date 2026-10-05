# =============================================================================
# CivicSense AI — YOLO Vision Detector
# =============================================================================
# Implements the VisionProvider interface using Ultralytics YOLOv8.
#
# Owner: Arpit (Person 1)
# =============================================================================

import time
from pathlib import Path

from ultralytics import YOLO

from app.core.interfaces import VisionProvider
from app.contracts.vision import VisionResult, Detection, BoundingBox
from app.vision.preprocessing import download_image, assess_and_decode_image
from app.core.logging import get_logger
from app.core.errors import ModelNotLoadedError
from app.config import get_settings

logger = get_logger(__name__)


class YOLODetector(VisionProvider):
    """
    Production-ready Vision Detector using Ultralytics YOLO.
    Downloads the image, assesses quality, runs inference, and formats outputs.
    """

    def __init__(self, model_path: str | None = None):
        settings = get_settings()
        self.model_path = model_path or settings.yolo_model_path
        self.model_version = Path(self.model_path).stem
        self._model = None
        self._load_model()

    def _load_model(self):
        """Load the YOLO model strictly from the configured path."""
        path = Path(self.model_path)
        
        try:
            # If the user explicitly configures "yolov8n.pt" for testing, ultralytics 
            # will handle downloading it. Otherwise, if it's a local path that doesn't 
            # exist, we want to fail loudly rather than silently falling back.
            if not path.exists() and not self.model_path.endswith('.pt') and "/" in self.model_path:
                raise FileNotFoundError(f"Model weights not found at {self.model_path}")
                
            logger.info(f"Loading YOLO model from: {self.model_path}")
            self._model = YOLO(self.model_path)
            logger.info(f"YOLO model '{self.model_path}' loaded successfully.")
            
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            raise ModelNotLoadedError(f"YOLO ({self.model_path})")

    async def detect(self, image_path: str) -> VisionResult:
        """
        Run vision detection pipeline on an image URL or local path.
        """
        start_time = time.time()
        
        # 1. Download / Load
        if image_path.startswith("http"):
            image_bytes = await download_image(image_path)
        else:
            try:
                with open(image_path, "rb") as f:
                    image_bytes = f.read()
            except IOError as e:
                raise Exception(f"Failed to read local image: {e}")

        # 2. Preprocess & Assess Quality
        image_bgr, quality = assess_and_decode_image(image_bytes)

        # 3. Inference
        if not self._model:
            raise ModelNotLoadedError(f"YOLO ({self.model_path})")

        # We proceed with inference even if quality issues are found to extract whatever we can,
        # but the decision engine may later reject it based on `is_valid`.
        results = self._model.predict(source=image_bgr, verbose=False)
        
        # 4. Parse Results
        raw_detections = []
        result = results[0] # Single image
        
        if result.boxes:
            boxes = result.boxes
            for i in range(len(boxes)):
                box = boxes[i]
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                class_name = self._model.names[cls_id]
                
                # xyxy format: x_min, y_min, x_max, y_max
                x1, y1, x2, y2 = map(float, box.xyxy[0])
                
                raw_detections.append(Detection(
                    issue_class=class_name.replace(" ", "_"),
                    confidence=conf,
                    bounding_box=BoundingBox(
                        x_min=x1, y_min=y1, x_max=x2, y_max=y2
                    )
                ))
                
        # 5. Classify and Filter
        from app.vision.classifier import classify_detections
        primary_issue, secondary_issues, class_status = classify_detections(raw_detections)
        
        elapsed_ms = (time.time() - start_time) * 1000

        return VisionResult(
            detections=raw_detections,
            primary_issue=primary_issue,
            secondary_issues=secondary_issues,
            image_quality=quality,
            classification_status=class_status,
            processing_time_ms=elapsed_ms,
            model_version=self.model_version,
            source="yolov8",
        )
