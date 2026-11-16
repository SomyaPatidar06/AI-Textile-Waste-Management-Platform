"""
AITEX Spatial Defect Annotation and Dataset Preparation.

Processes the raw AITEX fabric defect database into structured spatial annotations
with pixel masks, ground-truth bounding boxes, platform taxonomy mapping, and stratified
train/val/test splits.
"""

import json
import os
import random
from pathlib import Path
from typing import Any, Dict, List, Tuple
import cv2
import numpy as np


TAXONOMY_MAPPING = {
    "00": "Weave Defect",    # Broken end / warp defect
    "01": "Weave Defect",    # Broken pick / weft defect
    "02": "Hole",            # Weave hole / puncture
    "03": "Stain",           # Oil stain / spot
    "04": "Pinched Fabric",  # Pilling / fuzzy yarn
    "05": "Weave Defect",    # Thick bar
    "06": "Weave Defect",    # Thin bar
    "08": "Broken Stitch",   # Fly yarn / loose stitch
}


def extract_mask_boxes(mask_path: str, min_area: int = 15) -> List[Dict[str, Any]]:
    """Extract bounding boxes from a binary mask image using connected components."""
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    if mask is None:
        return []

    _, thresh = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(thresh)
    H, W = mask.shape
    boxes = []

    for i in range(1, num_labels):
        x, y, w, h, area = stats[i]
        if area >= min_area:
            boxes.append({
                "x": int(x),
                "y": int(y),
                "width": int(w),
                "height": int(h),
                "area": int(area),
                "box_2d": [
                    round(y / H, 4),
                    round(x / W, 4),
                    round((y + h) / H, 4),
                    round((x + w) / W, 4)
                ]
            })
    return boxes


def prepare_aitex_dataset(
    data_dir: str,
    output_dir: str,
    seed: int = 42
) -> Dict[str, Any]:
    """Generates structured spatial dataset and splits from AITEX files."""
    data_path = Path(data_dir)
    defect_dir = data_path / "Defect_images"
    mask_dir = data_path / "Mask_images"
    nodefect_dir = data_path / "NODefect_images"

    records: List[Dict[str, Any]] = []

    # 1. Process Defective Images
    defect_files = sorted(defect_dir.glob("*.png"))
    for img_file in defect_files:
        stem = img_file.stem
        code = stem.split("_")[-1] if "_" in stem else "02"
        defect_label = TAXONOMY_MAPPING.get(code, "Weave Defect")

        mask_file = mask_dir / f"{stem}_mask.png"
        boxes = []
        if mask_file.exists():
            boxes = extract_mask_boxes(str(mask_file))

        records.append({
            "image_id": stem,
            "filename": img_file.name,
            "relative_path": str(img_file.relative_to(data_path.parent)).replace("\\", "/"),
            "defect_code": code,
            "primary_label": defect_label,
            "is_defective": True,
            "width": 4096,
            "height": 256,
            "num_defects": len(boxes),
            "bounding_boxes": [
                {**b, "label": defect_label} for b in boxes
            ]
        })

    # 2. Process Clean / Defect-Free Images
    clean_files = sorted(nodefect_dir.glob("**/*.png"))
    for img_file in clean_files:
        stem = img_file.stem
        records.append({
            "image_id": stem,
            "filename": img_file.name,
            "relative_path": str(img_file.relative_to(data_path.parent)).replace("\\", "/"),
            "defect_code": "NONE",
            "primary_label": "Defect Free",
            "is_defective": False,
            "width": 4096,
            "height": 256,
            "num_defects": 0,
            "bounding_boxes": []
        })

    # 3. Stratified Split (70% train, 15% val, 15% test)
    rng = random.Random(seed)
    by_class: Dict[str, List[Dict[str, Any]]] = {}
    for r in records:
        lbl = r["primary_label"]
        by_class.setdefault(lbl, []).append(r)

    train_set, val_set, test_set = [], [], []

    for lbl, group in sorted(by_class.items()):
        rng.shuffle(group)
        n = len(group)
        n_train = max(1, int(round(n * 0.70)))
        n_val = max(1, int(round(n * 0.15))) if n > 3 else (1 if n > 1 else 0)
        n_test = n - n_train - n_val
        if n_test < 0:
            n_val = max(0, n_val + n_test)
            n_test = 0

        train_set.extend(group[:n_train])
        val_set.extend(group[n_train:n_train + n_val])
        test_set.extend(group[n_train + n_val:])

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    with open(out_path / "aitex_annotations.json", "w") as f:
        json.dump(records, f, indent=2)

    with open(out_path / "aitex_train.json", "w") as f:
        json.dump(train_set, f, indent=2)

    with open(out_path / "aitex_val.json", "w") as f:
        json.dump(val_set, f, indent=2)

    with open(out_path / "aitex_test.json", "w") as f:
        json.dump(test_set, f, indent=2)

    stats = {
        "total_images": len(records),
        "defective_images": len(defect_files),
        "defect_free_images": len(clean_files),
        "train_count": len(train_set),
        "val_count": len(val_set),
        "test_count": len(test_set),
        "total_bounding_boxes": sum(r["num_defects"] for r in records),
        "class_counts": {k: len(v) for k, v in by_class.items()}
    }

    with open(out_path / "aitex_dataset_manifest.json", "w") as f:
        json.dump(stats, f, indent=2)

    return stats


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent.parent
    data_dir = base_dir / "data" / "aitex_defect"
    output_dir = data_dir / "processed"
    result = prepare_aitex_dataset(str(data_dir), str(output_dir))
    print("AITEX dataset preparation complete:")
    print(json.dumps(result, indent=2))
