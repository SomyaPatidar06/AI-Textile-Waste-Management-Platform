"""
Defect Classification and Inspection Engine.

Integrates fine-tuned ResNet-18 defect characterization and spatial bounding box
localization across platform defect taxonomies.
"""

import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from torchvision import models, transforms

from app.core.config import settings
from app.ai.base import BaseDefectDetector, PredictionResult
from app.ai.spatial_detector import SpatialDefectDetector


class DefectEngine(BaseDefectDetector):
    """Deep learning textile defect detection and classification engine."""

    TAXONOMY = [
        "Defect Free",
        "Weave Defect",
        "Hole",
        "Stain",
        "Pinched Fabric",
        "Broken Stitch"
    ]

    def __init__(
        self,
        model_version: Optional[str] = None,
        weights_path: Optional[str] = None,
        labels_path: Optional[str] = None,
        device: Optional[str] = None
    ):
        self.model_version = model_version or settings.DEFECT_MODEL_VERSION
        self.spatial_detector = SpatialDefectDetector(
            weights_path=weights_path,
            labels_path=labels_path,
            device=device
        )

    def _calculate_entropy(self, probs: Dict[str, float]) -> float:
        k = len(probs)
        if k <= 1:
            return 0.0
        entropy = -sum(p * math.log(p) for p in probs.values() if p > 0)
        return entropy / math.log(k)

    def predict(self, image: Image.Image, threshold: Optional[float] = None) -> PredictionResult:
        active_threshold = threshold if threshold is not None else settings.DEFECT_CONFIDENCE_THRESHOLD

        detection_result = self.spatial_detector.detect(image, threshold=active_threshold)

        primary_label = detection_result["primary_defect"]
        confidence = detection_result["confidence"]
        bounding_boxes = detection_result["bounding_boxes"]

        # Approximate class distribution from spatial detector
        probs = {cat: 0.01 for cat in self.TAXONOMY}
        if primary_label in probs:
            probs[primary_label] = confidence
        rem = max(0.0, 1.0 - confidence)
        other_cats = [c for c in self.TAXONOMY if c != primary_label]
        for c in other_cats:
            probs[c] = rem / max(1, len(other_cats))

        sorted_probs = sorted(probs.items(), key=lambda kv: kv[1], reverse=True)
        margin = sorted_probs[0][1] - (sorted_probs[1][1] if len(sorted_probs) > 1 else 0.0)
        entropy = self._calculate_entropy(probs)

        is_uncertain = detection_result["is_uncertain"]
        reasons: List[str] = []

        if confidence < active_threshold:
            is_uncertain = True
            reasons.append(f"Confidence ({confidence:.2f}) below threshold ({active_threshold:.2f})")

        if margin < settings.AI_UNCERTAINTY_MARGIN:
            is_uncertain = True
            reasons.append(f"Low margin between classes ({margin:.2f})")

        if entropy > settings.AI_UNCERTAINTY_ENTROPY:
            is_uncertain = True
            reasons.append(f"High prediction entropy ({entropy:.2f})")

        if detection_result.get("uncertainty_reason"):
            reasons.append(detection_result["uncertainty_reason"])

        uncertainty_reason = " | ".join(reasons) if reasons else None

        return PredictionResult(
            label=primary_label,
            confidence=round(confidence, 4),
            is_uncertain=is_uncertain,
            requires_manual_inspection=is_uncertain,
            uncertainty_reason=uncertainty_reason,
            raw_probabilities={k: round(v, 4) for k, v in probs.items()},
            model_version=self.model_version,
            threshold_used=active_threshold,
            metadata={
                "margin": round(margin, 4),
                "normalized_entropy": round(entropy, 4),
                "num_defects": len(bounding_boxes),
                "bounding_boxes": bounding_boxes,
                "spatial_localization": "Image-Level Classification Only - Spatial Defect Localization Active",
                "latency_ms": detection_result["latency_ms"]
            }
        )
