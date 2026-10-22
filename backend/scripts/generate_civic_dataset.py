# =============================================================================
# CivicSense AI — Civic Issue Dataset Generator
# =============================================================================
# Generates a synthetic, geometrically authentic annotated dataset for fine-tuning
# YOLOv8 on CivicSense civic issue classes:
# 0: pothole
# 1: garbage_dump
# 2: broken_streetlight
# 3: road_damage
# 4: water_logging
# 5: fallen_tree
# =============================================================================

import os
import random
import yaml
from pathlib import Path
import cv2
import numpy as np

CLASS_NAMES = [
    "pothole",
    "garbage_dump",
    "broken_streetlight",
    "road_damage",
    "water_logging",
    "fallen_tree"
]

def create_road_background(width: int = 640, height: int = 640) -> np.ndarray:
    """Generate realistic textured asphalt / road surface."""
    base_color = random.randint(55, 95)
    img = np.full((height, width, 3), base_color, dtype=np.uint8)
    
    # Asphalt grain noise
    noise = np.random.normal(0, 12, (height, width, 3)).astype(np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    # Subtle road lane or curb edge occasionally
    if random.random() > 0.5:
        line_color = random.choice([(200, 200, 200), (40, 180, 220)]) # White or yellow
        pt1 = (random.randint(0, width // 4), 0)
        pt2 = (random.randint(0, width // 4), height)
        cv2.line(img, pt1, pt2, line_color, thickness=random.randint(4, 10))
        
    return img

def draw_pothole(img: np.ndarray, x: int, y: int, w: int, h: int):
    """Render an irregular dark asphalt cavity with depth shadows and cracked border."""
    center = (x + w // 2, y + h // 2)
    axes = (w // 2, h // 2)
    angle = random.randint(-25, 25)
    
    # Outer jagged contour
    num_pts = 16
    pts = []
    for i in range(num_pts):
        theta = 2 * np.pi * i / num_pts
        r_x = (w // 2) * (1 + random.uniform(-0.18, 0.18))
        r_y = (h // 2) * (1 + random.uniform(-0.18, 0.18))
        px = int(center[0] + r_x * np.cos(theta))
        py = int(center[1] + r_y * np.sin(theta))
        pts.append([px, py])
    poly = np.array([pts], dtype=np.int32)
    
    # Deep cavity core
    cv2.fillPoly(img, poly, (random.randint(18, 30), random.randint(18, 30), random.randint(18, 30)))
    # Inner shadow
    cv2.ellipse(img, (center[0] - 2, center[1] - 2), (max(2, w // 3), max(2, h // 3)), angle, 0, 360, (10, 10, 10), -1)
    # Jagged rim crack
    cv2.polylines(img, poly, True, (40, 40, 40), thickness=2)

def draw_garbage_dump(img: np.ndarray, x: int, y: int, w: int, h: int):
    """Render irregular clusters of waste, plastic bags, and debris."""
    colors = [
        (30, 30, 180),   # Red wrappers
        (180, 180, 30),  # Cyan / plastic
        (40, 180, 40),   # Green scraps
        (220, 220, 220), # White bags
        (20, 20, 20),    # Black bags
        (120, 100, 80),  # Cardboard
    ]
    
    num_items = random.randint(15, 30)
    for _ in range(num_items):
        item_w = random.randint(max(8, w // 8), max(12, w // 3))
        item_h = random.randint(max(8, h // 8), max(12, h // 3))
        item_x = random.randint(x, max(x + 1, x + w - item_w))
        item_y = random.randint(y, max(y + 1, y + h - item_h))
        color = random.choice(colors)
        
        shape = random.choice(["rect", "circle", "poly"])
        if shape == "circle":
            cv2.circle(img, (item_x + item_w // 2, item_y + item_h // 2), item_w // 2, color, -1)
        elif shape == "rect":
            cv2.rectangle(img, (item_x, item_y), (item_x + item_w, item_y + item_h), color, -1)
        else:
            pts = np.array([
                [item_x, item_y + item_h // 2],
                [item_x + item_w // 2, item_y],
                [item_x + item_w, item_y + item_h // 3],
                [item_x + 3 * item_w // 4, item_y + item_h],
                [item_x + item_w // 4, item_y + item_h]
            ], np.int32)
            cv2.fillPoly(img, [pts], color)

def draw_broken_streetlight(img: np.ndarray, x: int, y: int, w: int, h: int):
    """Render vertical metal pole with bent arm, broken luminaire, dangling wire."""
    pole_x = x + w // 2
    cv2.line(img, (pole_x, y + h), (pole_x, y + int(h * 0.25)), (140, 140, 150), thickness=max(3, w // 8))
    
    # Bent / fractured arm
    arm_end = (x + w - 4, y + int(h * 0.15))
    cv2.line(img, (pole_x, y + int(h * 0.25)), arm_end, (110, 110, 120), thickness=max(2, w // 10))
    
    # Broken luminaire housing
    cv2.rectangle(img, (arm_end[0] - 8, arm_end[1]), (arm_end[0] + 8, arm_end[1] + 12), (70, 70, 75), -1)
    # Exposed dangling wire
    pts = np.array([
        [arm_end[0], arm_end[1] + 12],
        [arm_end[0] - 4, arm_end[1] + 20],
        [arm_end[0] + 3, arm_end[1] + 28]
    ], np.int32)
    cv2.polylines(img, [pts], False, (20, 20, 180), thickness=2)

def draw_road_damage(img: np.ndarray, x: int, y: int, w: int, h: int):
    """Render spiderweb cracking and longitudinal road surface fractures."""
    num_cracks = random.randint(4, 8)
    for _ in range(num_cracks):
        start_x = random.randint(x, x + w)
        start_y = random.randint(y, y + h)
        cur_x, cur_y = start_x, start_y
        
        pts = [[cur_x, cur_y]]
        for _ in range(random.randint(4, 8)):
            cur_x += random.randint(-18, 18)
            cur_y += random.randint(-18, 18)
            cur_x = np.clip(cur_x, x, x + w)
            cur_y = np.clip(cur_y, y, y + h)
            pts.append([cur_x, cur_y])
            
        cv2.polylines(img, [np.array(pts, np.int32)], False, (random.randint(20, 40), random.randint(20, 40), random.randint(20, 40)), thickness=random.randint(2, 4))

def draw_water_logging(img: np.ndarray, x: int, y: int, w: int, h: int):
    """Render murky standing pool of water with reflections and ripple ellipses."""
    center = (x + w // 2, y + h // 2)
    # Semi-transparent overlay for water puddle
    overlay = img.copy()
    cv2.ellipse(overlay, center, (w // 2, h // 2), random.randint(-10, 10), 0, 360, (130, 110, 70), -1)
    cv2.addWeighted(overlay, 0.65, img, 0.35, 0, img)
    
    # Puddle ripples
    for r in range(1, 4):
        cv2.ellipse(img, center, (max(2, (w // 2) - r * 10), max(2, (h // 2) - r * 6)), 0, 0, 360, (160, 140, 100), 1)

def draw_fallen_tree(img: np.ndarray, x: int, y: int, w: int, h: int):
    """Render thick fallen timber trunk with side branches and green foliage obstructing roadway."""
    p1 = (x + 5, y + h - 10)
    p2 = (x + w - 5, y + 10)
    
    # Brown timber trunk
    cv2.line(img, p1, p2, (35, 55, 95), thickness=max(6, min(w, h) // 7))
    
    # Offshoot branches
    mid = ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)
    cv2.line(img, mid, (mid[0] + random.randint(-20, 20), mid[1] - random.randint(15, 30)), (30, 50, 85), thickness=max(2, min(w, h) // 14))
    
    # Foliage clumps
    for _ in range(random.randint(5, 10)):
        clump_x = random.randint(x, x + w)
        clump_y = random.randint(y, y + h)
        cv2.circle(img, (clump_x, clump_y), random.randint(8, 18), (random.randint(20, 50), random.randint(90, 150), random.randint(20, 60)), -1)

DRAW_FUNCS = {
    0: draw_pothole,
    1: draw_garbage_dump,
    2: draw_broken_streetlight,
    3: draw_road_damage,
    4: draw_water_logging,
    5: draw_fallen_tree
}

def generate_dataset(base_dir: Path, num_train: int = 150, num_val: int = 40):
    """Generate train and val image sets with corresponding YOLO txt annotations."""
    for split, count in [("train", num_train), ("val", num_val)]:
        img_dir = base_dir / "images" / split
        lbl_dir = base_dir / "labels" / split
        img_dir.mkdir(parents=True, exist_ok=True)
        lbl_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Generating {count} samples for {split}...")
        for idx in range(count):
            img = create_road_background(640, 640)
            labels = []
            
            # Select 1 to 2 civic issues per image
            num_issues = random.choice([1, 1, 1, 2])
            for _ in range(num_issues):
                cls_id = random.randint(0, 5)
                # Object size: 15% to 50% of image dimension
                obj_w = random.randint(120, 320)
                obj_h = random.randint(120, 320)
                if cls_id == 2: # Streetlight is taller than wide
                    obj_w = random.randint(90, 180)
                    obj_h = random.randint(240, 420)
                
                obj_x = random.randint(20, max(21, 640 - obj_w - 20))
                obj_y = random.randint(20, max(21, 640 - obj_h - 20))
                
                # Draw visual defect
                DRAW_FUNCS[cls_id](img, obj_x, obj_y, obj_w, obj_h)
                
                # Convert to normalized YOLO coordinates
                x_center = (obj_x + obj_w / 2.0) / 640.0
                y_center = (obj_y + obj_h / 2.0) / 640.0
                norm_w = obj_w / 640.0
                norm_h = obj_h / 640.0
                labels.append(f"{cls_id} {x_center:.6f} {y_center:.6f} {norm_w:.6f} {norm_h:.6f}")
                
            # Save image
            img_path = img_dir / f"civic_{split}_{idx:04d}.jpg"
            cv2.imwrite(str(img_path), img)
            
            # Save label file
            lbl_path = lbl_dir / f"civic_{split}_{idx:04d}.txt"
            with open(lbl_path, "w") as f:
                f.write("\n".join(labels) + "\n")
                
    # Create data.yaml
    yaml_content = {
        "path": str(base_dir.resolve()),
        "train": "images/train",
        "val": "images/val",
        "names": {i: name for i, name in enumerate(CLASS_NAMES)}
    }
    yaml_path = base_dir / "data.yaml"
    with open(yaml_path, "w") as f:
        yaml.dump(yaml_content, f, sort_keys=False)
        
    print(f"Dataset successfully created at {base_dir}")
    print(f"data.yaml written to {yaml_path}")

if __name__ == "__main__":
    dataset_dir = Path(__file__).resolve().parents[1] / "datasets" / "civic_dataset"
    generate_dataset(dataset_dir, num_train=180, num_val=45)
