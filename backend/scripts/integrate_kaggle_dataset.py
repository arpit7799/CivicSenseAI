# =============================================================================
# CivicSense AI — Kaggle Civic Dataset Integrator
# =============================================================================
# Integrates the 9 Kaggle sub-datasets into backend/datasets/civic_dataset:
# 1. Traverses all category directories for splits: train, valid, test
# 2. Standardizes label format (converts polygon annotations to bounding boxes)
# 3. Moves images and writes standardized labels to civic_dataset
# 4. Updates data.yaml and config.yaml with the 10 classes
# 5. Removes New_dataset after successful integration
# =============================================================================

import os
import shutil
import glob
from pathlib import Path
import yaml

ROOT_DIR = Path(__file__).resolve().parents[2]
NEW_DATASET_DIR = ROOT_DIR / "New_dataset"
TARGET_DATASET_DIR = ROOT_DIR / "backend" / "datasets" / "civic_dataset"
CONFIG_YAML = ROOT_DIR / "config.yaml"

CLASS_NAMES = {
    0: "Damaged Road issues",
    1: "Pothole Issues",
    2: "Illegal Parking Issues",
    3: "Broken Road Sign Issues",
    4: "Fallen trees",
    5: "Littering/Garbage on Public Places",
    6: "Vandalism Issues",
    7: "Dead Animal Pollution",
    8: "Damaged concrete structures",
    9: "Damaged Electric wires and poles",
}


def polygon_to_bbox(coords: list[float]) -> tuple[float, float, float, float]:
    """Convert polygon [x1, y1, x2, y2, ...] to YOLO [x_center, y_center, w, h]."""
    xs = coords[0::2]
    ys = coords[1::2]
    min_x = max(0.0, min(xs))
    max_x = min(1.0, max(xs))
    min_y = max(0.0, min(ys))
    max_y = min(1.0, max(ys))
    
    w = max(0.001, max_x - min_x)
    h = max(0.001, max_y - min_y)
    x_c = min(1.0, max(0.0, (min_x + max_x) / 2.0))
    y_c = min(1.0, max(0.0, (min_y + max_y) / 2.0))
    return x_c, y_c, w, h


def standardize_label_file(src_path: Path, dst_path: Path) -> int:
    """Read label, convert any polygon rows to bounding box rows, and write to dst."""
    clean_lines = []
    if src_path.exists():
        with open(src_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                parts = line.strip().split()
                if not parts:
                    continue
                try:
                    cls_id = int(parts[0])
                    coords = [float(p) for p in parts[1:]]
                    if len(coords) == 4:
                        # Standard YOLO bounding box: x_c, y_c, w, h
                        x_c, y_c, w, h = coords
                        # Clip to [0, 1]
                        x_c = min(1.0, max(0.0, x_c))
                        y_c = min(1.0, max(0.0, y_c))
                        w = min(1.0, max(0.001, w))
                        h = min(1.0, max(0.001, h))
                    elif len(coords) >= 6:
                        # Polygon segmentation -> convert to bounding box
                        x_c, y_c, w, h = polygon_to_bbox(coords)
                    else:
                        continue
                    clean_lines.append(f"{cls_id} {x_c:.6f} {y_c:.6f} {w:.6f} {h:.6f}")
                except (ValueError, IndexError):
                    continue

    dst_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dst_path, "w", encoding="utf-8") as f:
        if clean_lines:
            f.write("\n".join(clean_lines) + "\n")
        else:
            f.write("")
    return len(clean_lines)


def integrate_dataset():
    if not NEW_DATASET_DIR.exists():
        print(f"Error: {NEW_DATASET_DIR} does not exist.")
        return False

    print("=" * 65)
    print("CivicSense AI — Integrating Kaggle Dataset into civic_dataset")
    print(f"Source: {NEW_DATASET_DIR}")
    print(f"Target: {TARGET_DATASET_DIR}")
    print("=" * 65)

    # Ensure target dirs exist
    for split in ["train", "valid", "test"]:
        (TARGET_DATASET_DIR / "images" / split).mkdir(parents=True, exist_ok=True)
        (TARGET_DATASET_DIR / "labels" / split).mkdir(parents=True, exist_ok=True)

    category_dirs = [d for d in NEW_DATASET_DIR.iterdir() if d.is_dir()]
    total_images_moved = 0
    total_labels_processed = 0

    for cat_dir in sorted(category_dirs):
        # Category subfolder usually has an inner folder with the same name
        sub_dirs = [s for s in cat_dir.iterdir() if s.is_dir()]
        inner_dir = sub_dirs[0] if sub_dirs else cat_dir

        print(f"\nProcessing category: {cat_dir.name}...")

        for split in ["train", "valid", "test"]:
            src_img_dir = inner_dir / split / "images"
            src_lbl_dir = inner_dir / split / "labels"

            dst_img_dir = TARGET_DATASET_DIR / "images" / split
            dst_lbl_dir = TARGET_DATASET_DIR / "labels" / split

            if not src_img_dir.exists():
                continue

            images = list(src_img_dir.glob("*.jpg")) + list(src_img_dir.glob("*.png")) + list(src_img_dir.glob("*.jpeg"))
            split_count = 0

            for img_path in images:
                lbl_path = src_lbl_dir / f"{img_path.stem}.txt"
                dst_img_path = dst_img_dir / img_path.name
                dst_lbl_path = dst_lbl_dir / f"{img_path.stem}.txt"

                # Move image
                shutil.move(str(img_path), str(dst_img_path))
                total_images_moved += 1
                split_count += 1

                # Standardize and save label
                standardize_label_file(lbl_path, dst_lbl_path)
                total_labels_processed += 1

            print(f"  [{split}]: {split_count} images & labels integrated")

    # Create 'val' symlinks pointing to 'valid' for YOLO compatibility
    val_img_link = TARGET_DATASET_DIR / "images" / "val"
    val_lbl_link = TARGET_DATASET_DIR / "labels" / "val"

    if val_img_link.exists() or val_img_link.is_symlink():
        if val_img_link.is_symlink():
            val_img_link.unlink()
        elif val_img_link.is_dir():
            shutil.rmtree(val_img_link)
    os.symlink("valid", str(val_img_link), target_is_directory=True)

    if val_lbl_link.exists() or val_lbl_link.is_symlink():
        if val_lbl_link.is_symlink():
            val_lbl_link.unlink()
        elif val_lbl_link.is_dir():
            shutil.rmtree(val_lbl_link)
    os.symlink("valid", str(val_lbl_link), target_is_directory=True)

    # Clean old cache files
    for cache_f in TARGET_DATASET_DIR.glob("**/*.cache"):
        try:
            cache_f.unlink()
        except Exception:
            pass

    # Update data.yaml
    data_yaml_content = {
        "path": str(TARGET_DATASET_DIR.resolve()),
        "train": "images/train",
        "val": "images/valid",
        "test": "images/test",
        "names": CLASS_NAMES,
    }

    target_data_yaml = TARGET_DATASET_DIR / "data.yaml"
    with open(target_data_yaml, "w", encoding="utf-8") as f:
        yaml.dump(data_yaml_content, f, sort_keys=False)

    # Also update root config.yaml
    with open(CONFIG_YAML, "w", encoding="utf-8") as f:
        yaml.dump(data_yaml_content, f, sort_keys=False)

    print("\n" + "=" * 65)
    print(f"Dataset Integration Complete!")
    print(f"Total Images Integrated: {total_images_moved}")
    print(f"Total Labels Standardized: {total_labels_processed}")
    print(f"Updated: {target_data_yaml}")
    print(f"Updated: {CONFIG_YAML}")
    print("=" * 65)

    # Delete New_dataset directory
    print(f"\nDeleting temporary {NEW_DATASET_DIR} as requested...")
    shutil.rmtree(NEW_DATASET_DIR)
    print(f"Successfully deleted {NEW_DATASET_DIR}")
    return True


if __name__ == "__main__":
    integrate_dataset()

