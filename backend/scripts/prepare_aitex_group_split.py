"""
AITEX Group-Based (Loom-Independent) Dataset Preparation and Evaluation.

Guarantees 100% group isolation:
- No physical fabric roll or loom batch is shared across train, validation, or test.
- Evaluates the deployed models on genuinely unseen physical fabrics.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any

# Ensure backend in sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.ai.spatial_detector import SpatialDefectDetector
import torch
from torchvision import models, transforms
from PIL import Image
import numpy as np

TAXONOMY_MAPPING = {
    "00": "Weave Defect",
    "01": "Weave Defect",
    "02": "Hole",
    "03": "Stain",
    "04": "Pinched Fabric",
    "05": "Weave Defect",
    "06": "Weave Defect",
    "08": "Broken Stitch",
}

def create_group_split():
    repo_root = backend_dir.parent
    data_dir = repo_root / "data" / "aitex_defect"
    output_dir = data_dir / "processed"
    
    # 1. Partition Defective Fabric Rolls
    train_defect_rolls = {"016", "019", "023", "025", "027", "029", "030", "036"}
    val_defect_rolls = {"006", "022"}
    test_defect_rolls = {"002", "010"}
    
    # Verify zero overlap
    assert len(train_defect_rolls.intersection(val_defect_rolls)) == 0
    assert len(train_defect_rolls.intersection(test_defect_rolls)) == 0
    assert len(val_defect_rolls.intersection(test_defect_rolls)) == 0
    
    # 2. Partition Clean Loom Batches
    clean_dir = data_dir / "NODefect_images"
    clean_subdirs = sorted([d.name for d in clean_dir.iterdir() if d.is_dir()])
    
    train_clean_dirs = set(clean_subdirs[:5])
    val_clean_dirs = {clean_subdirs[5]}
    test_clean_dirs = {clean_subdirs[6]}
    
    # 3. Read existing annotations
    with open(output_dir / "aitex_annotations.json", "r") as f:
        all_records = json.load(f)
        
    train_set = []
    val_set = []
    test_set = []
    
    for r in all_records:
        if r["is_defective"]:
            roll = r["image_id"].split("_")[1]
            if roll in train_defect_rolls:
                train_set.append({**r, "group_id": f"roll_{roll}"})
            elif roll in val_defect_rolls:
                val_set.append({**r, "group_id": f"roll_{roll}"})
            elif roll in test_defect_rolls:
                test_set.append({**r, "group_id": f"roll_{roll}"})
        else:
            rel = r["relative_path"]
            # e.g. data/aitex_defect/NODefect_images/2306881-210020u/0001_000_05.png
            parts = rel.replace("\\", "/").split("/")
            batch_dir = parts[2] if len(parts) > 2 else "unknown"
            if batch_dir in train_clean_dirs:
                train_set.append({**r, "group_id": f"clean_{batch_dir}"})
            elif batch_dir in val_clean_dirs:
                val_set.append({**r, "group_id": f"clean_{batch_dir}"})
            elif batch_dir in test_clean_dirs:
                test_set.append({**r, "group_id": f"clean_{batch_dir}"})
                
    manifest = {
        "split_strategy": "Group-Based Physical Roll Isolation (Zero Leakage)",
        "train_defective_rolls": sorted(list(train_defect_rolls)),
        "val_defective_rolls": sorted(list(val_defect_rolls)),
        "test_defective_rolls": sorted(list(test_defect_rolls)),
        "train_clean_batches": sorted(list(train_clean_dirs)),
        "val_clean_batches": sorted(list(val_clean_dirs)),
        "test_clean_batches": sorted(list(test_clean_dirs)),
        "counts": {
            "train": len(train_set),
            "val": len(val_set),
            "test": len(test_set),
            "total": len(all_records)
        },
        "defect_counts": {
            "train_defect": sum(1 for s in train_set if s["is_defective"]),
            "val_defect": sum(1 for s in val_set if s["is_defective"]),
            "test_defect": sum(1 for s in test_set if s["is_defective"]),
            "train_clean": sum(1 for s in train_set if not s["is_defective"]),
            "val_clean": sum(1 for s in val_set if not s["is_defective"]),
            "test_clean": sum(1 for s in test_set if not s["is_defective"])
        }
    }
    
    with open(output_dir / "aitex_group_train.json", "w") as f:
        json.dump(train_set, f, indent=2)
    with open(output_dir / "aitex_group_val.json", "w") as f:
        json.dump(val_set, f, indent=2)
    with open(output_dir / "aitex_group_test.json", "w") as f:
        json.dump(test_set, f, indent=2)
    with open(output_dir / "aitex_group_split_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
        
    print(f"Group Split Complete:")
    print(f"  Train: {len(train_set)} (Defective: {manifest['defect_counts']['train_defect']}, Clean: {manifest['defect_counts']['train_clean']})")
    print(f"  Val:   {len(val_set)} (Defective: {manifest['defect_counts']['val_defect']}, Clean: {manifest['defect_counts']['val_clean']})")
    print(f"  Test:  {len(test_set)} (Defective: {manifest['defect_counts']['test_defect']}, Clean: {manifest['defect_counts']['test_clean']})")
    
    # 4. Evaluate Deployed Model on this Group-Held-Out Test Set
    print("\n--- Evaluating SpatialDefectDetector on Group-Held-Out Test Set ---")
    detector = SpatialDefectDetector()
    
    tp_defect = 0
    fn_defect = 0
    tn_clean = 0
    fp_clean = 0
    
    gt_boxes_covered = 0
    total_gt_boxes = 0
    
    for s in test_set:
        img_path = repo_root / "data" / s["relative_path"]
        res = detector.detect(img_path)
        pred_label = res["primary_defect"]
        pred_boxes = res["bounding_boxes"]
        gt_boxes = s["bounding_boxes"]
        
        if s["is_defective"]:
            total_gt_boxes += len(gt_boxes)
            if pred_label != "Defect Free":
                tp_defect += 1
            else:
                fn_defect += 1
            for gb in gt_boxes:
                if any(detector.compute_iou(pb["box_2d"], gb["box_2d"]) > 0.0 for pb in pred_boxes):
                    gt_boxes_covered += 1
        else:
            if pred_label == "Defect Free" or len(pred_boxes) == 0:
                tn_clean += 1
            else:
                fp_clean += 1
                
    n_def = manifest['defect_counts']['test_defect']
    n_clean = manifest['defect_counts']['test_clean']
    
    eval_result = {
        "test_rolls": sorted(list(test_defect_rolls)),
        "test_clean_batches": sorted(list(test_clean_dirs)),
        "defective_sample_count": n_def,
        "clean_sample_count": n_clean,
        "defective_roll_recall": round(tp_defect / max(1, n_def), 4),
        "defective_roll_fnr": round(fn_defect / max(1, n_def), 4),
        "clean_roll_specificity": round(tn_clean / max(1, n_clean), 4),
        "clean_roll_fpr": round(fp_clean / max(1, n_clean), 4),
        "total_gt_boxes": total_gt_boxes,
        "gt_boxes_intersected": gt_boxes_covered,
        "gt_coverage_rate": round(gt_boxes_covered / max(1, total_gt_boxes), 4)
    }
    
    with open(repo_root / "docs" / "phase-9" / "group_split_eval_results.json", "w") as f:
        json.dump(eval_result, f, indent=2)
        
    print("\nGroup-Held-Out Evaluation Findings:")
    print(f"  Defective Roll Detection Recall:  {eval_result['defective_roll_recall']*100:.2f}% ({tp_defect}/{n_def})")
    print(f"  Clean Roll True Specificity:      {eval_result['clean_roll_specificity']*100:.2f}% ({tn_clean}/{n_clean})")
    print(f"  Clean False Positive Rate:        {eval_result['clean_roll_fpr']*100:.2f}%")
    print(f"  Ground Truth Box Region Coverage: {eval_result['gt_coverage_rate']*100:.2f}% ({gt_boxes_covered}/{total_gt_boxes})")
    
    return manifest, eval_result

if __name__ == "__main__":
    create_group_split()
