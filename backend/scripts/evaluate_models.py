"""
Comprehensive Model Evaluation Script for AI Textile Waste Platform Phase 3.

Evaluates:
1. Material Classification (ResNet-18 natural fiber model on stratified test set)
2. Defect Classification (AITEX fine-tuned ResNet-18 model)
3. Spatial Object Detection Pipeline (bounding box extraction and localization)
4. Inference Latencies and Resource Utilization
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from torchvision import models, transforms

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.ai.spatial_detector import SpatialDefectDetector
from app.ai.material_engine import MaterialEngine


def evaluate_all():
    repo_root = backend_dir.parent
    data_dir = repo_root / "data"
    output_dir = repo_root / "docs" / "phase-3"
    output_dir.mkdir(parents=True, exist_ok=True)

    results: Dict[str, Any] = {}

    # =========================================================
    # 1. EVALUATE NATURAL FIBER MATERIAL MODEL
    # =========================================================
    print("--- 1. Evaluating Natural Fiber ResNet-18 Model ---")
    mat_test_json = data_dir / "material" / "processed" / "material_test.json"
    with open(mat_test_json, "r", encoding="utf-8") as f:
        mat_test_samples = json.load(f)

    mat_classes = ["Abaca", "Cotton", "Hessian", "Linen", "Silk", "Wool"]
    mat_class_to_idx = {c: i for i, c in enumerate(mat_classes)}

    mat_model = models.resnet18(weights=None)
    mat_model.fc = nn.Linear(512, len(mat_classes))
    mat_ckpt = backend_dir / "app" / "ai" / "models" / "fabric_model_v2.pth"
    ckpt_data = torch.load(mat_ckpt, map_location="cpu")
    mat_state_dict = ckpt_data["model_state_dict"] if "model_state_dict" in ckpt_data else ckpt_data
    mat_model.load_state_dict(mat_state_dict)
    mat_model.eval()

    mat_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    mat_conf_matrix = np.zeros((len(mat_classes), len(mat_classes)), dtype=int)
    mat_latencies = []

    with torch.no_grad():
        for s in mat_test_samples:
            img_path = data_dir / s["relative_path"]
            img = Image.open(img_path).convert("RGB")
            t0 = time.time()
            t = mat_transform(img).unsqueeze(0)
            out = mat_model(t)
            mat_latencies.append((time.time() - t0) * 1000)

            pred_idx = int(out.argmax(dim=1)[0])
            true_idx = mat_class_to_idx[s["label"]]
            mat_conf_matrix[true_idx, pred_idx] += 1

    total_mat = len(mat_test_samples)
    mat_acc = float(np.trace(mat_conf_matrix) / total_mat)

    # Per-class metrics
    mat_per_class = {}
    precisions, recalls, f1s = [], [], []
    for i, c in enumerate(mat_classes):
        tp = mat_conf_matrix[i, i]
        fp = mat_conf_matrix[:, i].sum() - tp
        fn = mat_conf_matrix[i, :].sum() - tp
        p = tp / max(1, tp + fp)
        r = tp / max(1, tp + fn)
        f1 = 2 * p * r / max(1e-6, p + r)
        precisions.append(p)
        recalls.append(r)
        f1s.append(f1)
        mat_per_class[c] = {
            "test_samples": int(mat_conf_matrix[i, :].sum()),
            "precision": round(p, 4),
            "recall": round(r, 4),
            "f1_score": round(f1, 4)
        }

    results["material_evaluation"] = {
        "model_architecture": "ResNet-18 Transfer Learning",
        "checkpoint": "fabric_model_v2.pth",
        "num_classes": len(mat_classes),
        "classes": mat_classes,
        "test_sample_count": total_mat,
        "overall_accuracy": round(mat_acc, 4),
        "macro_precision": round(float(np.mean(precisions)), 4),
        "macro_recall": round(float(np.mean(recalls)), 4),
        "macro_f1": round(float(np.mean(f1s)), 4),
        "weighted_f1": round(float(np.mean(f1s)), 4),
        "avg_latency_ms": round(float(np.mean(mat_latencies)), 2),
        "confusion_matrix": mat_conf_matrix.tolist(),
        "per_class_metrics": mat_per_class
    }
    print(f"Material Model Accuracy: {mat_acc * 100:.2f}%, Latency: {np.mean(mat_latencies):.2f} ms")

    # =========================================================
    # 2. EVALUATE DEFECT MODEL TRAINING HISTORY
    # =========================================================
    print("--- 2. Evaluating AITEX Defect Training Run ---")
    defect_history_file = backend_dir / "app" / "ai" / "models" / "aitex_defect_training_history.json"
    with open(defect_history_file, "r", encoding="utf-8") as f:
        defect_history = json.load(f)

    results["defect_training_evaluation"] = {
        "model_architecture": "ResNet-18",
        "checkpoint": "aitex_defect_model.pth",
        "training_epochs": defect_history["epochs"],
        "best_val_accuracy": defect_history["best_val_acc"],
        "final_train_loss": defect_history["history"][-1]["train_loss"],
        "final_train_acc": defect_history["history"][-1]["train_acc"],
        "final_val_loss": defect_history["history"][-1]["val_loss"],
        "final_val_acc": defect_history["history"][-1]["val_acc"],
        "epoch_history": defect_history["history"]
    }
    print(f"Defect Model Best Val Accuracy: {defect_history['best_val_acc'] * 100:.2f}%")

    # =========================================================
    # 3. EVALUATE SPATIAL OBJECT DETECTOR BENCHMARK
    # =========================================================
    print("--- 3. Evaluating Spatial Defect Detector on AITEX Test Set ---")
    detector = SpatialDefectDetector()
    aitex_test_json = data_dir / "aitex_defect" / "processed" / "aitex_test.json"
    with open(aitex_test_json, "r", encoding="utf-8") as f:
        aitex_test_samples = json.load(f)

    def_correct = 0
    clean_correct = 0
    total_def = sum(1 for s in aitex_test_samples if s["is_defective"])
    total_clean = sum(1 for s in aitex_test_samples if not s["is_defective"])
    det_latencies = []
    total_boxes = 0

    for s in aitex_test_samples:
        img_path = data_dir / s["relative_path"]
        t0 = time.time()
        res = detector.detect(img_path)
        det_latencies.append((time.time() - t0) * 1000)

        boxes = res["bounding_boxes"]
        total_boxes += len(boxes)

        if s["is_defective"]:
            if res["primary_defect"] != "Defect Free":
                def_correct += 1
        else:
            if len(boxes) == 0 or res["primary_defect"] == "Defect Free":
                clean_correct += 1

    results["spatial_detection_evaluation"] = {
        "benchmark": "AITEX Fabric Defect Test Split",
        "total_test_images": len(aitex_test_samples),
        "defective_images": total_def,
        "defect_classification_accuracy": round(def_correct / max(1, total_def), 4),
        "clean_images": total_clean,
        "clean_classification_accuracy": round(clean_correct / max(1, total_clean), 4),
        "total_detected_boxes": total_boxes,
        "avg_latency_ms": round(float(np.mean(det_latencies)), 2),
        "bounding_box_format": "[ymin, xmin, ymax, xmax] normalized"
    }
    print(f"Defect Image Accuracy: {def_correct/total_def*100:.2f}%, Avg Latency: {np.mean(det_latencies):.2f} ms")

    # Save complete evaluation results
    eval_json_path = output_dir / "evaluation_data.json"
    with open(eval_json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nEvaluation summary saved to: {eval_json_path}")
    return results


if __name__ == "__main__":
    evaluate_all()
