# =============================================================================
# CivicSense AI — YOLOv8 Civic Model Trainer
# =============================================================================
# Fine-tunes Ultralytics YOLOv8 on the CivicSense civic issues dataset:
# - pothole
# - garbage_dump
# - broken_streetlight
# - road_damage
# - water_logging
# - fallen_tree
#
# Saves the resulting fine-tuned model to ai-service/models/civicsense_yolo.pt
# =============================================================================

import os
import shutil
from pathlib import Path
from ultralytics import YOLO
import torch

def train_civicsense_yolo():
    base_dir = Path(__file__).resolve().parents[1]
    dataset_yaml = base_dir / "datasets" / "civic_dataset" / "data.yaml"
    weights_path = base_dir / "yolov8n.pt"
    models_dir = base_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    target_model_path = models_dir / "civicsense_yolo.pt"
    
    if not dataset_yaml.exists():
        raise FileNotFoundError(f"Dataset config not found at {dataset_yaml}")
        
    print("=" * 60)
    print("CivicSense AI — YOLO Training Pipeline")
    print(f"Base Weights: {weights_path}")
    print(f"Dataset YAML: {dataset_yaml}")
    print(f"Target Output: {target_model_path}")
    print("=" * 60)
    
    # Check device: use MPS if available on Mac, otherwise CPU
    if torch.backends.mps.is_available():
        device = "mps"
        print("Using Apple Silicon GPU acceleration (device='mps')")
    elif torch.cuda.is_available():
        device = "cuda"
        print("Using CUDA GPU acceleration")
    else:
        device = "cpu"
        print("Using CPU device")
        
    # Load base YOLO model
    model = YOLO(str(weights_path))
    
    # Train model
    runs_dir = base_dir / "models" / "training_runs"
    results = model.train(
        data=str(dataset_yaml),
        epochs=10,
        imgsz=640,
        batch=8,
        device=device,
        project=str(runs_dir),
        name="civicsense_yolo_run",
        exist_ok=True,
        verbose=True,
        plots=True,
    )
    
    # Path to best weights
    best_weights = runs_dir / "civicsense_yolo_run" / "weights" / "best.pt"
    if not best_weights.exists():
        best_weights = runs_dir / "civicsense_yolo_run" / "weights" / "last.pt"
        
    if best_weights.exists():
        shutil.copy(best_weights, target_model_path)
        print("\n" + "=" * 60)
        print(f"Training Complete! Best model saved to: {target_model_path}")
        print("=" * 60)
    else:
        raise FileNotFoundError("Training completed but no weight file was generated.")
        
    # Validation metrics
    print("\nRunning Model Validation on Held-Out Validation Set...")
    val_results = model.val()
    print("Validation Metrics:")
    print(f"  - mAP50: {val_results.box.map50:.4f}")
    print(f"  - mAP50-95: {val_results.box.map:.4f}")
    
    # Test sample inference
    test_img = base_dir / "datasets" / "civic_dataset" / "images" / "val" / "civic_val_0000.jpg"
    if test_img.exists():
        print(f"\nRunning test inference on {test_img.name}...")
        infer_model = YOLO(str(target_model_path))
        test_pred = infer_model.predict(source=str(test_img), verbose=False)
        boxes = test_pred[0].boxes
        print(f"Detected {len(boxes)} civic issue(s):")
        for i, box in enumerate(boxes):
            cls_name = infer_model.names[int(box.cls[0])]
            conf = float(box.conf[0])
            print(f"  {i+1}. {cls_name} (confidence: {conf:.2f})")
            
    return target_model_path

if __name__ == "__main__":
    train_civicsense_yolo()
