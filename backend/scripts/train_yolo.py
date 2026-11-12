# =============================================================================
# CivicSense AI — YOLOv8 10-Class Civic Model Trainer
# =============================================================================
# Fine-tunes Ultralytics YOLOv8 on the 10-class CivicSense civic issues dataset:
#  0: Damaged Road issues
#  1: Pothole Issues
#  2: Illegal Parking Issues
#  3: Broken Road Sign Issues
#  4: Fallen trees
#  5: Littering/Garbage on Public Places
#  6: Vandalism Issues
#  7: Dead Animal Pollution
#  8: Damaged concrete structures
#  9: Damaged Electric wires and poles
#
# Saves the resulting fine-tuned model to backend/models/civicsense_yolo.pt
# =============================================================================

import argparse
import os
import shutil
from collections import defaultdict
from pathlib import Path
import yaml
import torch

os.environ["YOLO_CONFIG_DIR"] = "/tmp"
from ultralytics import YOLO


def create_balanced_manifest(data_yaml_path: Path, samples_per_class: int = 30) -> Path:
    """Creates a temporary balanced dataset YAML pointing to text files of image paths."""
    base_dir = data_yaml_path.parent
    with open(data_yaml_path) as f:
        config = yaml.safe_load(f)

    labels_train_dir = base_dir / "labels" / "train"
    labels_val_dir = base_dir / "labels" / "valid"

    def select_images(labels_dir: Path, max_per_class: int) -> list[str]:
        class_images = defaultdict(list)
        for label_file in sorted(labels_dir.glob("*.txt")):
            try:
                with open(label_file) as f:
                    file_classes = set()
                    for line in f:
                        parts = line.strip().split()
                        if parts:
                            file_classes.add(int(parts[0]))
                    
                    img_path = str(label_file).replace("/labels/", "/images/").rsplit(".", 1)[0] + ".jpg"
                    if os.path.exists(img_path):
                        for c in file_classes:
                            if len(class_images[c]) < max_per_class:
                                class_images[c].append(img_path)
            except Exception:
                continue

        selected = set()
        for c in range(10):
            selected.update(class_images[c])
        return sorted(list(selected))

    train_imgs = select_images(labels_train_dir, samples_per_class)
    val_imgs = select_images(labels_val_dir, max(5, samples_per_class // 3))

    manifest_dir = base_dir / "manifests"
    manifest_dir.mkdir(exist_ok=True)

    train_txt = manifest_dir / "train_subset.txt"
    val_txt = manifest_dir / "val_subset.txt"

    with open(train_txt, "w") as f:
        for p in train_imgs:
            f.write(f"{p}\n")

    with open(val_txt, "w") as f:
        for p in val_imgs:
            f.write(f"{p}\n")

    subset_yaml = manifest_dir / "subset_data.yaml"
    subset_config = {
        "path": str(base_dir),
        "train": str(train_txt),
        "val": str(val_txt),
        "names": config.get("names", {})
    }
    with open(subset_yaml, "w") as f:
        yaml.dump(subset_config, f)

    print(f"Created balanced subset: {len(train_imgs)} train images, {len(val_imgs)} val images.")
    return subset_yaml


def train_civicsense_yolo(epochs: int = 5, batch: int = 16, samples_per_class: int = 30, full_dataset: bool = False):
    base_dir = Path(__file__).resolve().parents[1]
    dataset_yaml = base_dir / "datasets" / "civic_dataset" / "data.yaml"
    weights_path = base_dir / "yolov8n.pt"
    models_dir = base_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    target_model_path = models_dir / "civicsense_yolo.pt"

    if not dataset_yaml.exists():
        raise FileNotFoundError(f"Dataset config not found at {dataset_yaml}")

    # Determine data source
    if full_dataset or samples_per_class <= 0:
        training_yaml = dataset_yaml
        print("Training on FULL dataset (38,000+ images)...")
    else:
        print(f"Training on balanced subset ({samples_per_class} samples/class)...")
        training_yaml = create_balanced_manifest(dataset_yaml, samples_per_class=samples_per_class)

    print("=" * 60)
    print("CivicSense AI — 10-Class YOLO Training Pipeline")
    print(f"Base Weights: {weights_path}")
    print(f"Training YAML: {training_yaml}")
    print(f"Target Output: {target_model_path}")
    print(f"Epochs: {epochs}, Batch Size: {batch}")
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
        data=str(training_yaml),
        epochs=epochs,
        imgsz=640,
        batch=batch,
        device=device,
        project=str(runs_dir),
        name="civicsense_yolo_run",
        exist_ok=True,
        verbose=True,
        plots=False,
    )

    # Path to best weights
    best_weights = runs_dir / "civicsense_yolo_run" / "weights" / "best.pt"
    if not best_weights.exists():
        best_weights = runs_dir / "civicsense_yolo_run" / "weights" / "last.pt"

    if best_weights.exists():
        shutil.copy(best_weights, target_model_path)
        print("\n" + "=" * 60)
        print(f"Training Complete! Model saved to: {target_model_path}")
        print("=" * 60)
    else:
        raise FileNotFoundError("Training completed but no weight file was generated.")

    # Validation metrics
    print("\nRunning Model Validation on Held-Out Validation Set...")
    val_results = model.val()
    print("Validation Metrics:")
    print(f"  - mAP50: {val_results.box.map50:.4f}")
    print(f"  - mAP50-95: {val_results.box.map:.4f}")

    # Test sample inference on first available validation image
    val_images_dir = base_dir / "datasets" / "civic_dataset" / "images" / "valid"
    sample_images = list(val_images_dir.glob("*.jpg"))
    if sample_images:
        test_img = sample_images[0]
        print(f"\nRunning test inference on sample {test_img.name}...")
        infer_model = YOLO(str(target_model_path))
        test_pred = infer_model.predict(source=str(test_img), verbose=False)
        boxes = test_pred[0].boxes
        print(f"Detected {len(boxes)} civic issue(s):")
        for i, box in enumerate(boxes):
            cls_id = int(box.cls[0])
            cls_name = infer_model.names.get(cls_id, f"class_{cls_id}")
            conf = float(box.conf[0])
            print(f"  {i+1}. {cls_name} (class {cls_id}, confidence: {conf:.2f})")

    return target_model_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CivicSense AI YOLO Model Trainer")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--samples-per-class", type=int, default=30, help="Balanced samples per class (default: 30)")
    parser.add_argument("--full", action="store_true", help="Train on full dataset")
    args = parser.parse_args()

    train_civicsense_yolo(
        epochs=args.epochs,
        batch=args.batch,
        samples_per_class=args.samples_per_class,
        full_dataset=args.full
    )
