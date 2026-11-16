import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
from app.ai.spatial_detector import SpatialDefectDetector

with open("../data/aitex_defect/processed/aitex_test.json") as f:
    test_samples = json.load(f)

def_samples = [s for s in test_samples if s["is_defective"]]
print(f"Total defective test samples: {len(def_samples)}")

detector = SpatialDefectDetector()

for idx, s in enumerate(def_samples[:5]):
    img_path = Path("../data") / s["relative_path"]
    gt_boxes = s["bounding_boxes"]
    res = detector.detect(img_path)
    pred_boxes = res["bounding_boxes"]
    print(f"\n--- Sample {idx+1}: {s['filename']} ({s['primary_label']}) ---")
    print("Ground Truth Boxes:", [b["box_2d"] for b in gt_boxes])
    print("Predicted Boxes:   ", [b["box_2d"] for b in pred_boxes])
    for p_i, pb in enumerate(pred_boxes):
        for g_i, gb in enumerate(gt_boxes):
            iou = detector.compute_iou(pb["box_2d"], gb["box_2d"])
            print(f"   Pred {p_i} vs GT {g_i}: IoU = {iou:.4f}")
