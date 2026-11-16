"""
Phase 4.1 AI Reliability Audit and Evaluation Script.

Executes comprehensive verification across:
1. Material Classifier (ResNet-18 natural fiber model) on untouched test split.
2. Defect Classifier (ResNet-18 AITEX model) on true independent held-out test split.
3. Model Calibration (Expected Calibration Error, Brier Score).
4. Spatial Defect Detector localization, IoU, and clean-image false positive rates across thresholds.
5. Cotton/Silk ambiguity and uncertainty gating audit.
"""

import json
import math
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import cv2
import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from sklearn.metrics import classification_report, confusion_matrix
from torchvision import models, transforms

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.ai.spatial_detector import SpatialDefectDetector
from app.ai.material_engine import MaterialEngine
from app.ai.defect_engine import DefectEngine


def calculate_ece(probs: np.ndarray, labels: np.ndarray, n_bins: int = 10) -> float:
    """Calculates Expected Calibration Error (ECE) for multi-class predictions."""
    confidences = np.max(probs, axis=1)
    predictions = np.argmax(probs, axis=1)
    accuracies = (predictions == labels).astype(float)

    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0

    for i in range(n_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]
        in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
        prop_in_bin = np.mean(in_bin)

        if prop_in_bin > 0:
            accuracy_in_bin = np.mean(accuracies[in_bin])
            avg_confidence_in_bin = np.mean(confidences[in_bin])
            ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin

    return float(ece)


def calculate_brier_score(probs: np.ndarray, labels: np.ndarray, num_classes: int) -> float:
    """Calculates multi-class Brier score."""
    one_hot = np.zeros((len(labels), num_classes))
    for i, l in enumerate(labels):
        one_hot[i, l] = 1.0
    return float(np.mean(np.sum((probs - one_hot) ** 2, axis=1)))


def audit_material_model(repo_root: Path) -> Dict[str, Any]:
    print("\n========================================================")
    print("1. AUDITING MATERIAL CLASSIFIER (ResNet-18)")
    print("========================================================")
    data_dir = repo_root / "data"
    test_json = data_dir / "material" / "processed" / "material_test.json"
    with open(test_json, "r", encoding="utf-8") as f:
        test_samples = json.load(f)

    classes = ["Abaca", "Cotton", "Hessian", "Linen", "Silk", "Wool"]
    class_to_idx = {c: i for i, c in enumerate(classes)}

    model = models.resnet18(weights=None)
    model.fc = nn.Linear(512, len(classes))
    ckpt_path = backend_dir / "app" / "ai" / "models" / "fabric_model_v2.pth"
    ckpt_data = torch.load(ckpt_path, map_location="cpu")
    state_dict = ckpt_data["model_state_dict"] if isinstance(ckpt_data, dict) and "model_state_dict" in ckpt_data else ckpt_data
    model.load_state_dict(state_dict)
    model.eval()

    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    all_probs = []
    all_preds = []
    all_targets = []
    latencies = []
    margins = []
    entropies = []

    with torch.no_grad():
        for s in test_samples:
            img_path = data_dir / s["relative_path"]
            img = Image.open(img_path).convert("RGB")
            t0 = time.time()
            tensor = transform(img).unsqueeze(0)
            logits = model(tensor)
            latencies.append((time.time() - t0) * 1000)

            p = torch.softmax(logits, dim=1).cpu().numpy()[0]
            all_probs.append(p)
            pred = int(np.argmax(p))
            all_preds.append(pred)
            target = class_to_idx[s["label"]]
            all_targets.append(target)

            # Dispersion metrics
            sorted_p = np.sort(p)[::-1]
            margin = float(sorted_p[0] - sorted_p[1])
            margins.append(margin)

            # Normalized Shannon entropy
            k = len(classes)
            ent = -np.sum([pi * math.log(pi) for pi in p if pi > 0]) / math.log(k)
            entropies.append(float(ent))

    all_probs = np.array(all_probs)
    all_preds = np.array(all_preds)
    all_targets = np.array(all_targets)

    acc = float(np.mean(all_preds == all_targets))
    cm = confusion_matrix(all_targets, all_preds).tolist()
    report = classification_report(all_targets, all_preds, target_names=classes, output_dict=True)
    ece = calculate_ece(all_probs, all_targets)
    brier = calculate_brier_score(all_probs, all_targets, len(classes))

    # Cotton vs Silk specific audit
    cotton_idx = class_to_idx["Cotton"]
    silk_idx = class_to_idx["Silk"]
    cotton_mask = (all_targets == cotton_idx)
    silk_mask = (all_targets == silk_idx)

    cotton_silk_confusions = int(np.sum((all_targets == cotton_idx) & (all_preds == silk_idx)))
    silk_cotton_confusions = int(np.sum((all_targets == silk_idx) & (all_preds == cotton_idx)))

    # Cotton samples that triggered uncertainty
    cotton_margins = [margins[i] for i in range(len(test_samples)) if cotton_mask[i]]
    cotton_entropies = [entropies[i] for i in range(len(test_samples)) if cotton_mask[i]]
    cotton_flagged = sum(1 for m, h in zip(cotton_margins, cotton_entropies) if m < 0.20 or h > 0.70)

    print(f"Material Test Accuracy: {acc * 100:.2f}% ({np.sum(all_preds == all_targets)}/{len(all_targets)})")
    print(f"Macro F1: {report['macro avg']['f1-score']:.4f}, Weighted F1: {report['weighted avg']['f1-score']:.4f}")
    print(f"ECE (Expected Calibration Error): {ece:.4f}")
    print(f"Brier Score: {brier:.4f}")
    print(f"Mean Latency: {np.mean(latencies):.2f} ms")
    print(f"Cotton misclassified as Silk: {cotton_silk_confusions}/23")
    print(f"Silk misclassified as Cotton: {silk_cotton_confusions}/23")
    print(f"Cotton samples gated by uncertainty: {cotton_flagged}/23 ({cotton_flagged/23*100:.1f}%)")

    return {
        "model_architecture": "ResNet-18",
        "checkpoint": "fabric_model_v2.pth",
        "test_sample_count": len(test_samples),
        "overall_accuracy": round(acc, 4),
        "macro_f1": round(report["macro avg"]["f1-score"], 4),
        "weighted_f1": round(report["weighted avg"]["f1-score"], 4),
        "ece": round(ece, 4),
        "brier_score": round(brier, 4),
        "avg_latency_ms": round(float(np.mean(latencies)), 2),
        "confusion_matrix": cm,
        "classification_report": report,
        "cotton_silk_analysis": {
            "cotton_as_silk": cotton_silk_confusions,
            "silk_as_cotton": silk_cotton_confusions,
            "cotton_uncertainty_flagged": cotton_flagged,
            "total_cotton_test": int(np.sum(cotton_mask)),
            "cotton_recall": round(report["Cotton"]["recall"], 4),
            "silk_precision": round(report["Silk"]["precision"], 4)
        }
    }


def audit_defect_classifier_independent_test(repo_root: Path) -> Dict[str, Any]:
    print("\n========================================================")
    print("2. AUDITING DEFECT CLASSIFIER ON INDEPENDENT HELD-OUT TEST SET")
    print("========================================================")
    data_dir = repo_root / "data"
    test_json = data_dir / "aitex_defect" / "processed" / "aitex_test.json"
    with open(test_json, "r", encoding="utf-8") as f:
        test_samples = json.load(f)

    classes = [
        "Defect Free",
        "Weave Defect",
        "Hole",
        "Stain",
        "Pinched Fabric",
        "Broken Stitch"
    ]
    class_to_idx = {c: i for i, c in enumerate(classes)}

    model = models.resnet18(weights=None)
    model.fc = nn.Linear(512, len(classes))
    ckpt_path = backend_dir / "app" / "ai" / "models" / "aitex_defect_model.pth"
    model.load_state_dict(torch.load(ckpt_path, map_location="cpu"))
    model.eval()

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    # Extract test patches from held-out rolls
    test_patches: List[Tuple[Image.Image, int, str]] = []
    for s in test_samples:
        img_path = data_dir / s["relative_path"]
        if not img_path.exists():
            continue
        full_img = Image.open(img_path).convert("RGB")
        w, h = full_img.size

        if not s["is_defective"] or len(s["bounding_boxes"]) == 0:
            # Clean roll: sample 2 clean crops
            for offset in [0, w // 2]:
                crop = full_img.crop((offset, 0, min(w, offset + h), h))
                test_patches.append((crop, class_to_idx["Defect Free"], "Defect Free"))
        else:
            # Defective roll: extract each ground-truth defect crop
            for b in s["bounding_boxes"]:
                lbl = b.get("label", s["primary_label"])
                if lbl not in class_to_idx:
                    lbl = "Weave Defect"

                bx, by, bw, bh = b["x"], b["y"], b["width"], b["height"]
                side = max(h, bw, bh)
                cx = bx + bw // 2
                cy = by + bh // 2
                x1 = max(0, cx - side // 2)
                y1 = max(0, cy - side // 2)
                x2 = min(w, x1 + side)
                y2 = min(h, y1 + side)
                defect_crop = full_img.crop((x1, y1, x2, y2))
                test_patches.append((defect_crop, class_to_idx[lbl], lbl))

            # Plus 1 clean background patch far from defect
            min_dx = min(b["x"] for b in s["bounding_boxes"])
            clean_x = 0 if min_dx > 500 else max(0, w - h)
            clean_crop = full_img.crop((clean_x, 0, clean_x + h, h))
            test_patches.append((clean_crop, class_to_idx["Defect Free"], "Defect Free"))

    all_probs = []
    all_preds = []
    all_targets = []
    latencies = []

    with torch.no_grad():
        for crop, target_idx, lbl in test_patches:
            t0 = time.time()
            tensor = transform(crop).unsqueeze(0)
            logits = model(tensor)
            latencies.append((time.time() - t0) * 1000)

            p = torch.softmax(logits, dim=1).cpu().numpy()[0]
            all_probs.append(p)
            pred = int(np.argmax(p))
            all_preds.append(pred)
            all_targets.append(target_idx)

    all_probs = np.array(all_probs)
    all_preds = np.array(all_preds)
    all_targets = np.array(all_targets)

    acc = float(np.mean(all_preds == all_targets))
    cm = confusion_matrix(all_targets, all_preds, labels=list(range(len(classes)))).tolist()
    report = classification_report(all_targets, all_preds, labels=list(range(len(classes))), target_names=classes, output_dict=True, zero_division=0)
    ece = calculate_ece(all_probs, all_targets)
    brier = calculate_brier_score(all_probs, all_targets, len(classes))

    print(f"Independent Held-Out Defect Test Accuracy: {acc * 100:.2f}% ({np.sum(all_preds == all_targets)}/{len(all_targets)})")
    print(f"Validation Accuracy was previously reported as: 97.65% (Best val at epoch 6)")
    print(f"Macro F1: {report['macro avg']['f1-score']:.4f}, Weighted F1: {report['weighted avg']['f1-score']:.4f}")
    print(f"ECE: {ece:.4f}, Brier Score: {brier:.4f}")
    print(f"Mean Latency: {np.mean(latencies):.2f} ms")

    return {
        "model_architecture": "ResNet-18",
        "checkpoint": "aitex_defect_model.pth",
        "held_out_test_patches": len(test_patches),
        "test_accuracy": round(acc, 4),
        "validation_accuracy_peak": 0.9765,
        "generalization_delta": round(0.9765 - acc, 4),
        "macro_f1": round(report["macro avg"]["f1-score"], 4),
        "weighted_f1": round(report["weighted avg"]["f1-score"], 4),
        "ece": round(ece, 4),
        "brier_score": round(brier, 4),
        "avg_latency_ms": round(float(np.mean(latencies)), 2),
        "confusion_matrix": cm,
        "classification_report": report
    }


def audit_spatial_detector(repo_root: Path) -> Dict[str, Any]:
    print("\n========================================================")
    print("3. AUDITING SPATIAL OBJECT DETECTOR (Localization, Masks & FPR)")
    print("========================================================")
    data_dir = repo_root / "data"
    test_json = data_dir / "aitex_defect" / "processed" / "aitex_test.json"
    with open(test_json, "r", encoding="utf-8") as f:
        test_samples = json.load(f)

    detector = SpatialDefectDetector()

    # Threshold sweep to analyze trade-off between Defect Recall and Clean FPR
    thresholds = [0.45, 0.55, 0.65, 0.75, 0.85]
    sweep_results = {}

    for thresh in thresholds:
        def_detected = 0
        clean_false_alarms = 0
        total_def = sum(1 for s in test_samples if s["is_defective"])
        total_clean = sum(1 for s in test_samples if not s["is_defective"])
        all_ious = []

        for s in test_samples:
            img_path = data_dir / s["relative_path"]
            res = detector.detect(img_path, threshold=thresh)
            boxes = res["bounding_boxes"]

            if s["is_defective"]:
                if len(boxes) > 0 and res["primary_defect"] != "Defect Free":
                    def_detected += 1

                # Calculate IoU against ground-truth boxes
                gt_boxes = s.get("bounding_boxes", [])
                for gt in gt_boxes:
                    gt_box = gt["box_2d"]
                    best_iou = 0.0
                    for det in boxes:
                        det_box = det["box_2d"]
                        iou = SpatialDefectDetector.compute_iou(det_box, gt_box)
                        if iou > best_iou:
                            best_iou = iou
                    all_ious.append(best_iou)
            else:
                if len(boxes) > 0 and res["primary_defect"] != "Defect Free":
                    clean_false_alarms += 1

        recall = def_detected / max(1, total_def)
        clean_fpr = clean_false_alarms / max(1, total_clean)
        clean_spec = 1.0 - clean_fpr
        mean_iou = float(np.mean(all_ious)) if all_ious else 0.0

        sweep_results[str(thresh)] = {
            "defect_recall": round(recall, 4),
            "clean_false_positive_rate": round(clean_fpr, 4),
            "clean_specificity": round(clean_spec, 4),
            "mean_iou_on_hits": round(mean_iou, 4)
        }
        print(f"Threshold {thresh:.2f} -> Defect Recall: {recall*100:.1f}%, Clean FPR: {clean_fpr*100:.1f}%, Clean Specificity: {clean_spec*100:.1f}%, Mean IoU: {mean_iou:.4f}")

    return {
        "benchmark": "AITEX Fabric Defect Test Split",
        "total_rolls": len(test_samples),
        "defective_rolls": sum(1 for s in test_samples if s["is_defective"]),
        "clean_rolls": sum(1 for s in test_samples if not s["is_defective"]),
        "threshold_sweep": sweep_results,
        "default_threshold_metrics": sweep_results["0.45"]
    }


def main():
    repo_root = backend_dir.parent
    mat_results = audit_material_model(repo_root)
    defect_results = audit_defect_classifier_independent_test(repo_root)
    spatial_results = audit_spatial_detector(repo_root)

    audit_summary = {
        "audit_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "material_model_audit": mat_results,
        "defect_model_audit": defect_results,
        "spatial_detector_audit": spatial_results
    }

    out_file = repo_root / "docs" / "phase-4" / "ai_reliability_audit_data.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(audit_summary, f, indent=2)

    print(f"\nAudit complete! Raw evaluation saved to {out_file}")


if __name__ == "__main__":
    main()
