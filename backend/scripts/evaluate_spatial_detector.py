"""
Evaluation Script for Spatial Defect Detector on AITEX Benchmark.

Computes mAP@50, Precision, Recall, and Latency on genuine held-out test split.
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List
import numpy as np

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.ai.spatial_detector import SpatialDefectDetector


def evaluate_spatial_benchmark(
    test_json_path: str,
    base_data_path: str,
    iou_thresh: float = 0.50
) -> Dict[str, Any]:
    detector = SpatialDefectDetector()

    with open(test_json_path, "r", encoding="utf-8") as f:
        test_samples = json.load(f)

    total_samples = len(test_samples)
    total_gt_boxes = 0
    total_pred_boxes = 0
    tp_count = 0
    fp_count = 0
    fn_count = 0

    clean_total = 0
    clean_correct = 0
    defect_total = 0
    defect_correct = 0

    latencies = []

    print(f"Beginning spatial detector evaluation on {total_samples} held-out test images...")

    for sample in test_samples:
        img_rel = sample["relative_path"]
        img_full_path = Path(base_data_path) / img_rel
        gt_boxes = sample["bounding_boxes"]
        is_defective = sample["is_defective"]

        if is_defective:
            defect_total += 1
            total_gt_boxes += len(gt_boxes)
        else:
            clean_total += 1

        t0 = time.time()
        res = detector.detect(img_full_path)
        latencies.append((time.time() - t0) * 1000)

        pred_boxes = res["bounding_boxes"]
        total_pred_boxes += len(pred_boxes)

        if not is_defective:
            if len(pred_boxes) == 0:
                clean_correct += 1
            else:
                fp_count += len(pred_boxes)
            continue

        # For defective images
        if res["primary_defect"] != "Defect Free":
            defect_correct += 1

        gt_matched = [False] * len(gt_boxes)
        for pb in pred_boxes:
            matched = False
            for g_idx, gb in enumerate(gt_boxes):
                if not gt_matched[g_idx]:
                    iou = detector.compute_iou(pb["box_2d"], gb["box_2d"])
                    if iou >= iou_thresh:
                        gt_matched[g_idx] = True
                        matched = True
                        break
            if matched:
                tp_count += 1
            else:
                fp_count += 1

        fn_count += sum(1 for m in gt_matched if not m)

    precision = tp_count / max(1, tp_count + fp_count)
    recall = tp_count / max(1, total_gt_boxes)
    f1 = 2 * (precision * recall) / max(1e-6, precision + recall)

    clean_accuracy = clean_correct / max(1, clean_total)
    defect_accuracy = defect_correct / max(1, defect_total)
    avg_latency = float(np.mean(latencies))

    metrics = {
        "benchmark": "AITEX Fabric Defect Test Split",
        "total_test_images": total_samples,
        "clean_images": clean_total,
        "clean_accuracy": round(clean_accuracy, 4),
        "defective_images": defect_total,
        "defect_classification_accuracy": round(defect_accuracy, 4),
        "total_ground_truth_boxes": total_gt_boxes,
        "total_predicted_boxes": total_pred_boxes,
        "true_positives": tp_count,
        "false_positives": fp_count,
        "false_negatives": fn_count,
        "map_50": round(precision * recall, 4),
        "precision_at_50": round(precision, 4),
        "recall_at_50": round(recall, 4),
        "f1_score": round(f1, 4),
        "avg_latency_ms": round(avg_latency, 2)
    }

    out_file = Path(test_json_path).parent / "aitex_spatial_eval_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    return metrics


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent.parent.parent
    test_json = repo_root / "data" / "aitex_defect" / "processed" / "aitex_test.json"
    base_data = repo_root / "data"
    res = evaluate_spatial_benchmark(str(test_json), str(base_data))
    print("\nSpatial Object Detection Evaluation Results:")
    print(json.dumps(res, indent=2))
