import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
from app.ai.spatial_detector import SpatialDefectDetector

with open("../data/aitex_defect/processed/aitex_test.json") as f:
    test_samples = json.load(f)

def_samples = [s for s in test_samples if s["is_defective"]]
detector = SpatialDefectDetector()

total_gt = 0
covered_gt_at_any_iou = 0
covered_gt_at_10 = 0
covered_gt_at_25 = 0
covered_gt_at_50 = 0

all_best_ious = []

for s in def_samples:
    img_path = Path("../data") / s["relative_path"]
    gt_boxes = s["bounding_boxes"]
    total_gt += len(gt_boxes)
    res = detector.detect(img_path)
    pred_boxes = res["bounding_boxes"]
    
    for gb in gt_boxes:
        best_iou = 0.0
        for pb in pred_boxes:
            iou = detector.compute_iou(pb["box_2d"], gb["box_2d"])
            if iou > best_iou:
                best_iou = iou
        all_best_ious.append(best_iou)
        if best_iou > 0.0:
            covered_gt_at_any_iou += 1
        if best_iou >= 0.10:
            covered_gt_at_10 += 1
        if best_iou >= 0.25:
            covered_gt_at_25 += 1
        if best_iou >= 0.50:
            covered_gt_at_50 += 1

print(f"Total Ground Truth Defect Instances: {total_gt}")
print(f"Defects with any intersecting predicted region (IoU > 0.0): {covered_gt_at_any_iou} ({covered_gt_at_any_iou/total_gt*100:.1f}%)")
print(f"Defects covered at IoU >= 0.10: {covered_gt_at_10} ({covered_gt_at_10/total_gt*100:.1f}%)")
print(f"Defects covered at IoU >= 0.25: {covered_gt_at_25} ({covered_gt_at_25/total_gt*100:.1f}%)")
print(f"Defects covered at IoU >= 0.50: {covered_gt_at_50} ({covered_gt_at_50/total_gt*100:.1f}%)")
print(f"Mean Best IoU across all GT defects: {sum(all_best_ious)/len(all_best_ious):.4f}")
print("Individual Best IoUs:", [round(x, 4) for x in all_best_ious])
