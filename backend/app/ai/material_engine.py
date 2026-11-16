"""
Material Classification Engine.

Implements deep learning fiber and textile classification using a fine-tuned ResNet-18
architecture with ImageNet normalization, uncertainty estimation, margin analysis, and
entropy threshold gating.

Taxonomy Scope:
The active neural checkpoint (fabric_model_v2.pth / .onnx) is strictly a 6-class natural
fiber classifier (Abaca, Cotton, Hessian, Linen, Silk, Wool).
Synthetic consignments (Polyester, Nylon, Denim, Leather, Viscose) are inventory declaration
options but cannot be reliably discriminated by this optical RGB model without lab testing.
Any input exhibiting high entropy (>0.75) or low confidence (<0.50) is gated as
'Unknown / Out-of-Distribution (Visual Estimate)' with mandatory operator inspection.
"""

import json
import math
from pathlib import Path
from typing import Dict, List, Optional

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
from app.ai.base import BaseMaterialClassifier, PredictionResult


class MaterialEngine(BaseMaterialClassifier):
    """Deep learning material characterization engine using fine-tuned ResNet-18."""

    NATURAL_TAXONOMY = [
        "Abaca",
        "Cotton",
        "Hessian",
        "Linen",
        "Silk",
        "Wool"
    ]

    COMMERCIAL_TAXONOMY = [
        "Cotton",
        "Polyester",
        "Poly-Cotton Blend",
        "Denim",
        "Wool",
        "Silk",
        "Linen",
        "Viscose",
        "Nylon",
        "Leather",
        "Mixed/Unknown"
    ]

    def __init__(
        self,
        model_version: Optional[str] = None,
        weights_path: Optional[str] = None,
        device: Optional[str] = None
    ):
        self.model_version = model_version or settings.MATERIAL_MODEL_VERSION
        base_dir = Path(__file__).resolve().parent / "models"

        if device:
            self.device = torch.device(device)
        else:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Prioritize certified natural fiber model, fall back to commercial classifier
        natural_weights = base_dir / "fabric_model_v2.pth"
        commercial_weights = base_dir / "material_classifier.pt"

        if weights_path:
            target_weights = Path(weights_path)
            self.taxonomy = self.COMMERCIAL_TAXONOMY if "material_classifier" in str(target_weights) else self.NATURAL_TAXONOMY
        elif natural_weights.exists():
            target_weights = natural_weights
            self.taxonomy = self.NATURAL_TAXONOMY
        elif commercial_weights.exists():
            target_weights = commercial_weights
            self.taxonomy = self.COMMERCIAL_TAXONOMY
        else:
            target_weights = None
            self.taxonomy = self.COMMERCIAL_TAXONOMY

        self.weights_path = target_weights
        self.model = self._load_model()
        self.is_production_certified = bool(
            self.weights_path and self.weights_path == natural_weights and "certified" in self.model_version.lower()
        )

        # Optional ONNX Runtime acceleration with safe PyTorch fallback
        self.onnx_session = None
        self.onnx_input_name = None
        onnx_file = base_dir / "fabric_model_v2.onnx"
        if HAS_ONNX and onnx_file.exists():
            try:
                opts = ort.SessionOptions()
                opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
                self.onnx_session = ort.InferenceSession(str(onnx_file), opts, providers=["CPUExecutionProvider"])
                self.onnx_input_name = self.onnx_session.get_inputs()[0].name
            except Exception:
                self.onnx_session = None

        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    def _load_model(self) -> Optional[nn.Module]:
        if not self.weights_path or not self.weights_path.exists():
            return None

        try:
            model = models.resnet18(weights=None)
            model.fc = nn.Linear(512, len(self.taxonomy))
            ckpt = torch.load(self.weights_path, map_location=self.device)
            state_dict = ckpt["model_state_dict"] if isinstance(ckpt, dict) and "model_state_dict" in ckpt else ckpt
            model.load_state_dict(state_dict)
            model.to(self.device)
            model.eval()
            return model
        except Exception:
            return None

    def _calculate_entropy(self, probs: Dict[str, float]) -> float:
        k = len(probs)
        if k <= 1:
            return 0.0
        entropy = -sum(p * math.log(p) for p in probs.values() if p > 0)
        return entropy / math.log(k)

    def predict(self, image: Image.Image) -> PredictionResult:
        img_rgb = image.convert("RGB")

        if self.model is None:
            # Fallback heuristic if checkpoint missing
            return self._heuristic_fallback(img_rgb)

        tensor = self.transform(img_rgb).unsqueeze(0)
        runtime_used = "PyTorch (CPU)"

        if self.onnx_session is not None:
            try:
                np_in = tensor.cpu().numpy()
                logits_np = self.onnx_session.run(None, {self.onnx_input_name: np_in})[0]
                exp_logits = np.exp(logits_np - np.max(logits_np, axis=1, keepdims=True))
                probs_np = (exp_logits / np.sum(exp_logits, axis=1, keepdims=True))[0]
                probs_list = probs_np.tolist()
                runtime_used = "ONNX Runtime (CPU)"
            except Exception:
                # Safe fallback to PyTorch on any ONNX error
                tensor_dev = tensor.to(self.device)
                with torch.no_grad():
                    logits = self.model(tensor_dev)
                    probs_t = torch.softmax(logits, dim=1)[0]
                    probs_list = probs_t.cpu().numpy().tolist()
        else:
            tensor_dev = tensor.to(self.device)
            with torch.no_grad():
                logits = self.model(tensor_dev)
                probs_t = torch.softmax(logits, dim=1)[0]
                probs_list = probs_t.cpu().numpy().tolist()

        probs = {cat: float(probs_list[i]) for i, cat in enumerate(self.taxonomy)}
        sorted_pairs = sorted(probs.items(), key=lambda kv: kv[1], reverse=True)

        primary_label, primary_conf = sorted_pairs[0]
        secondary_label, secondary_conf = sorted_pairs[1] if len(sorted_pairs) > 1 else ("", 0.0)

        margin = primary_conf - secondary_conf
        entropy = self._calculate_entropy(probs)

        is_uncertain = False
        reasons: List[str] = []

        is_ood = primary_conf < 0.50 or entropy > 0.75
        if is_ood:
            primary_label = "Unknown / Out-of-Distribution"
            is_uncertain = True
            reasons.append(f"Sample out-of-distribution or high visual ambiguity (confidence={primary_conf:.2f}, entropy={entropy:.2f})")
        else:
            if primary_conf < settings.DEFECT_CONFIDENCE_THRESHOLD:
                is_uncertain = True
                reasons.append(f"Confidence ({primary_conf:.2f}) below operational threshold ({settings.DEFECT_CONFIDENCE_THRESHOLD:.2f})")

            if margin < settings.AI_UNCERTAINTY_MARGIN:
                is_uncertain = True
                reasons.append(f"Low margin between classes ({margin:.2f})")

            if entropy > settings.AI_UNCERTAINTY_ENTROPY:
                is_uncertain = True
                reasons.append(f"High prediction entropy ({entropy:.2f})")

        uncertainty_reason = " | ".join(reasons) if reasons else None

        label_out = primary_label if self.is_production_certified and not is_ood else f"{primary_label} (Visual Estimate)"
        is_unc = is_uncertain or is_ood or not self.is_production_certified
        unc_reason = uncertainty_reason
        if not self.is_production_certified:
            policy_reason = "Option B Policy: Model pending empirical certification. Requires visual inspection."
            unc_reason = f"{uncertainty_reason} | {policy_reason}" if uncertainty_reason else policy_reason

        return PredictionResult(
            label=label_out,
            confidence=round(primary_conf, 4),
            is_uncertain=is_unc,
            requires_manual_inspection=is_unc,
            uncertainty_reason=unc_reason,
            raw_probabilities={k: round(v, 4) for k, v in probs.items()},
            model_version=self.model_version,
            threshold_used=settings.DEFECT_CONFIDENCE_THRESHOLD,
            metadata={
                "margin": round(margin, 4),
                "normalized_entropy": round(entropy, 4),
                "inference_runtime": runtime_used,
                "is_production_certified": self.is_production_certified,
                "is_out_of_distribution": is_ood,
                "architecture": "ResNet-18 Deep Transfer Learning (6 Natural Fiber Classes)",
                "taxonomy_scope": "Abaca, Cotton, Hessian, Linen, Silk, Wool",
                "disclaimer": "Deep learning visual fiber estimation strictly on natural fiber taxonomy; laboratory test required for certified purity and synthetic blends."
            }
        )

    def _heuristic_fallback(self, img_rgb: Image.Image) -> PredictionResult:
        w, h = img_rgb.size
        center_crop = img_rgb.crop((w * 0.25, h * 0.25, w * 0.75, h * 0.75)).resize((32, 32))
        pixels = list(center_crop.getdata())
        r_vals = [p[0] for p in pixels]
        mean_r = sum(r_vals) / len(r_vals)
        variance = (sum((r - mean_r) ** 2 for r in r_vals) / len(r_vals)) ** 0.5

        if variance > 40.0:
            primary = "Cotton"
            p1 = 0.55
        elif variance > 20.0:
            primary = "Linen"
            p1 = 0.48
        else:
            primary = "Silk"
            p1 = 0.50

        probs = {cat: 0.1 for cat in self.taxonomy}
        probs[primary] = p1

        return PredictionResult(
            label=f"{primary} (Visual Estimate)",
            confidence=round(p1, 4),
            is_uncertain=True,
            requires_manual_inspection=True,
            uncertainty_reason="Option B Policy: Model pending empirical certification. Requires visual inspection.",
            raw_probabilities={k: round(v, 4) for k, v in probs.items()},
            model_version=self.model_version,
            threshold_used=settings.DEFECT_CONFIDENCE_THRESHOLD,
            metadata={
                "margin": 0.2,
                "normalized_entropy": 0.8,
                "is_production_certified": False,
                "disclaimer": "Heuristic estimate only."
            }
        )
