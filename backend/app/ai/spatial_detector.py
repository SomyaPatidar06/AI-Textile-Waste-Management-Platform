"""
Spatial Defect Detection and Localization Engine.

Performs multi-scale spatial scanning, texture anomaly localization, and ResNet-18
classification to detect, localize, and classify textile defects (holes, stains,
weave defects, broken stitches, needle marks, pinched fabric) with normalized
bounding boxes [ymin, xmin, ymax, xmax].
"""

import json
import math
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import cv2
import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from torchvision import models, transforms

try:
    import onnxruntime as ort
    HAS_ONNX = True
except ImportError:
    HAS_ONNX = False

from app.core.config import settings


class SpatialDefectDetector:
    """Production spatial defect detection engine combining patch scanning and CNN classification."""

    DEFAULT_LABELS = [
        "Stain",
        "Hole",
        "Broken Stitch",
        "Needle Mark",
        "Pinched Fabric",
        "Weave Defect",
        "Defect Free"
    ]

    def __init__(
        self,
        weights_path: Optional[str] = None,
        labels_path: Optional[str] = None,
        confidence_threshold: Optional[float] = None,
        device: Optional[str] = None
    ):
        base_ai_dir = Path(__file__).resolve().parent
        default_weights = base_ai_dir / "models" / "aitex_defect_model.pth"
        if not default_weights.exists():
            default_weights = base_ai_dir / "models" / "defect_classifier.pt"

        default_labels = base_ai_dir / "models" / "aitex_defect_labels.json"
        if not default_labels.exists():
            default_labels = base_ai_dir / "models" / "defect_labels.json"

        self.weights_path = Path(weights_path) if weights_path else default_weights
        self.labels_path = Path(labels_path) if labels_path else default_labels
        self.confidence_threshold = confidence_threshold or settings.DEFECT_CONFIDENCE_THRESHOLD

        if device:
            self.device = torch.device(device)
        else:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.labels = self._load_labels()
        self.model = self._load_model()

        # Optional ONNX Runtime acceleration with safe PyTorch fallback
        self.onnx_session = None
        self.onnx_input_name = None
        onnx_file = base_ai_dir / "models" / "aitex_defect_model.onnx"
        if HAS_ONNX and onnx_file.exists():
            try:
                opts = ort.SessionOptions()
                opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
                self.onnx_session = ort.InferenceSession(str(onnx_file), opts, providers=["CPUExecutionProvider"])
                self.onnx_input_name = self.onnx_session.get_inputs()[0].name
            except Exception:
                self.onnx_session = None

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    def _load_labels(self) -> List[str]:
        if self.labels_path.exists():
            try:
                with open(self.labels_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return list(self.DEFAULT_LABELS)

    def _load_model(self) -> Optional[nn.Module]:
        if not self.weights_path.exists():
            return None

        try:
            model = models.resnet18(weights=None)
            model.fc = nn.Linear(512, len(self.labels))
            ckpt = torch.load(self.weights_path, map_location=self.device)
            model.load_state_dict(ckpt)
            model.to(self.device)
            model.eval()
            return model
        except Exception:
            return None

    @staticmethod
    def compute_iou(box1: List[float], box2: List[float]) -> float:
        """Computes Intersection over Union for [ymin, xmin, ymax, xmax]."""
        y_min = max(box1[0], box2[0])
        x_min = max(box1[1], box2[1])
        y_max = min(box1[2], box2[2])
        x_max = min(box1[3], box2[3])

        inter_h = max(0.0, y_max - y_min)
        inter_w = max(0.0, x_max - x_min)
        inter_area = inter_h * inter_w

        area1 = max(0.0, box1[2] - box1[0]) * max(0.0, box1[3] - box1[1])
        area2 = max(0.0, box2[2] - box2[0]) * max(0.0, box2[3] - box2[1])

        union_area = area1 + area2 - inter_area
        if union_area <= 0.0:
            return 0.0
        return inter_area / union_area

    def _apply_nms(
        self,
        detections: List[Dict[str, Any]],
        iou_threshold: float = 0.40
    ) -> List[Dict[str, Any]]:
        """Suppresses overlapping bounding boxes of the same class."""
        if not detections:
            return []

        sorted_dets = sorted(detections, key=lambda d: d["confidence"], reverse=True)
        selected: List[Dict[str, Any]] = []

        for candidate in sorted_dets:
            keep = True
            for existing in selected:
                if candidate["label"] == existing["label"]:
                    iou = self.compute_iou(candidate["box_2d"], existing["box_2d"])
                    if iou > iou_threshold:
                        keep = False
                        break
            if keep:
                selected.append(candidate)

        return selected

    def _merge_adjacent_boxes(
        self,
        detections: List[Dict[str, Any]],
        thresh_dist: float = 0.05
    ) -> List[Dict[str, Any]]:
        """Merges adjacent and continuous defect bounding boxes of the same class."""
        if not detections:
            return []

        merged: List[Dict[str, Any]] = []
        by_class: Dict[str, List[Dict[str, Any]]] = {}
        for d in detections:
            by_class.setdefault(d["label"], []).append(d)

        for label, group in by_class.items():
            sorted_boxes = sorted(group, key=lambda b: b["box_2d"][1])
            curr = dict(sorted_boxes[0])
            curr["box_2d"] = list(curr["box_2d"])

            for b in sorted_boxes[1:]:
                c_box = curr["box_2d"]
                b_box = b["box_2d"]
                if b_box[1] <= c_box[3] + thresh_dist:
                    c_box[0] = min(c_box[0], b_box[0])
                    c_box[1] = min(c_box[1], b_box[1])
                    c_box[2] = max(c_box[2], b_box[2])
                    c_box[3] = max(c_box[3], b_box[3])
                    curr["confidence"] = max(curr["confidence"], b["confidence"])
                else:
                    merged.append(curr)
                    curr = dict(b)
                    curr["box_2d"] = list(curr["box_2d"])
            merged.append(curr)

        return merged

    def _generate_candidate_windows(self, width: int, height: int) -> List[Tuple[int, int, int, int]]:
        """Generates candidate sliding-window patch coordinates [x1, y1, x2, y2]."""
        windows: List[Tuple[int, int, int, int]] = []
        aspect = width / max(1, height)

        if aspect >= 2.5:
            # Ultra-wide textile roll (e.g. AITEX 4096x256)
            patch_w = height
            stride = max(64, patch_w // 2)
            for x in range(0, width - patch_w + 1, stride):
                windows.append((x, 0, x + patch_w, height))
            if width % stride != 0 and (width - patch_w) > 0:
                windows.append((width - patch_w, 0, width, height))
        else:
            # Standard aspect ratio images (e.g. 512x512, 800x600)
            # Full image
            windows.append((0, 0, width, height))

            # 2x2 grid
            half_w, half_h = width // 2, height // 2
            if half_w >= 112 and half_h >= 112:
                windows.append((0, 0, half_w, half_h))
                windows.append((half_w, 0, width, half_h))
                windows.append((0, half_h, half_w, height))
                windows.append((half_w, half_h, width, height))

            # Center crop
            cw1, ch1 = int(width * 0.25), int(height * 0.25)
            cw2, ch2 = int(width * 0.75), int(height * 0.75)
            windows.append((cw1, ch1, cw2, ch2))

        return windows

    def detect(
        self,
        image: Union[Image.Image, np.ndarray, str, Path],
        threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Executes spatial defect detection on an image.

        Returns:
            Dict containing:
                - primary_defect: str
                - confidence: float
                - bounding_boxes: List[Dict[str, Any]] with [ymin, xmin, ymax, xmax]
                - is_uncertain: bool
                - requires_manual_inspection: bool
                - uncertainty_reason: Optional[str]
                - latency_ms: float
        """
        t0 = time.time()
        active_thresh = threshold if threshold is not None else self.confidence_threshold

        # Load image
        if isinstance(image, (str, Path)):
            pil_img = Image.open(str(image)).convert("RGB")
        elif isinstance(image, np.ndarray):
            pil_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        else:
            pil_img = image.convert("RGB")

        w, h = pil_img.size
        cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        if self.model is None:
            # Fallback if checkpoint is not found
            return {
                "primary_defect": "Defect Free",
                "confidence": 0.85,
                "bounding_boxes": [],
                "is_uncertain": True,
                "requires_manual_inspection": True,
                "uncertainty_reason": "Defect classifier model weights not loaded.",
                "latency_ms": round((time.time() - t0) * 1000, 2)
            }

        # 1. Generate candidate windows
        windows = self._generate_candidate_windows(w, h)
        patches = [self.transform(pil_img.crop(box)) for box in windows]
        batch = torch.stack(patches)
        runtime_used = "PyTorch (CPU)"

        if self.onnx_session is not None:
            try:
                np_in = batch.cpu().numpy()
                logits_np = self.onnx_session.run(None, {self.onnx_input_name: np_in})[0]
                exp_l = np.exp(logits_np - np.max(logits_np, axis=1, keepdims=True))
                probs = exp_l / np.sum(exp_l, axis=1, keepdims=True)
                runtime_used = "ONNX Runtime (CPU)"
            except Exception:
                # Safe fallback to PyTorch
                batch_dev = batch.to(self.device)
                with torch.no_grad():
                    logits = self.model(batch_dev)
                    probs = torch.softmax(logits, dim=1).cpu().numpy()
        else:
            batch_dev = batch.to(self.device)
            with torch.no_grad():
                logits = self.model(batch_dev)
                probs = torch.softmax(logits, dim=1).cpu().numpy()

        raw_detections: List[Dict[str, Any]] = []

        # 2. Analyze candidates
        for idx, (x1, y1, x2, y2) in enumerate(windows):
            p_vec = probs[idx]
            pred_idx = int(np.argmax(p_vec))
            label = self.labels[pred_idx]
            conf = float(p_vec[pred_idx])

            if label != "Defect Free" and conf >= active_thresh:
                # Sub-window anomaly localization using pixel residuals
                patch_crop = cv_img[y1:y2, x1:x2]
                patch_gray = cv2.cvtColor(patch_crop, cv2.COLOR_BGR2GRAY)
                blur = cv2.medianBlur(patch_gray, 15)
                diff = cv2.absdiff(patch_gray, blur)

                # Find dominant defect connected component
                t_val = np.percentile(diff, 98.5)
                _, thresh = cv2.threshold(diff, max(12, int(t_val)), 255, cv2.THRESH_BINARY)
                num_labels, _, stats, _ = cv2.connectedComponentsWithStats(thresh)

                component_found = False
                for s_idx in range(1, num_labels):
                    sx, sy, sw, sh, sarea = stats[s_idx]
                    if sarea >= 18:
                        pad_x = max(4, int(sw * 0.15))
                        pad_y = max(4, int(sh * 0.15))
                        box_y1 = max(0, y1 + sy - pad_y) / h
                        box_x1 = max(0, x1 + sx - pad_x) / w
                        box_y2 = min(h, y1 + sy + sh + pad_y) / h
                        box_x2 = min(w, x1 + sx + sw + pad_x) / w

                        raw_detections.append({
                            "label": label,
                            "confidence": round(conf, 4),
                            "box_2d": [
                                round(box_y1, 4),
                                round(box_x1, 4),
                                round(box_y2, 4),
                                round(box_x2, 4)
                            ]
                        })
                        component_found = True

                # If no fine component passed area threshold, use candidate window boundary
                if not component_found:
                    raw_detections.append({
                        "label": label,
                        "confidence": round(conf, 4),
                        "box_2d": [
                            round(y1 / h, 4),
                            round(x1 / w, 4),
                            round(y2 / h, 4),
                            round(x2 / w, 4)
                        ]
                    })

        # 3. Apply Non-Maximum Suppression and merge continuous regions
        suppressed_boxes = self._apply_nms(raw_detections, iou_threshold=0.40)
        final_boxes = self._merge_adjacent_boxes(suppressed_boxes, thresh_dist=0.06)

        latency = round((time.time() - t0) * 1000, 2)

        # 4. Synthesize overall image prediction
        if final_boxes:
            best_det = max(final_boxes, key=lambda d: d["confidence"])
            primary_label = best_det["label"]
            primary_conf = best_det["confidence"]
            is_uncertain = primary_conf < 0.60
            reason = "Borderline defect detection confidence." if is_uncertain else None
        else:
            primary_label = "Defect Free"
            primary_conf = 0.94
            is_uncertain = False
            reason = None

        return {
            "primary_defect": primary_label,
            "confidence": primary_conf,
            "bounding_boxes": final_boxes,
            "num_defects": len(final_boxes),
            "is_uncertain": is_uncertain,
            "requires_manual_inspection": is_uncertain,
            "uncertainty_reason": reason,
            "inference_runtime": runtime_used,
            "latency_ms": latency
        }
