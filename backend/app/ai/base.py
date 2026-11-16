from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Optional, Any
from PIL import Image


@dataclass
class PredictionResult:
    """Standardized representation of an AI model inference output."""
    label: str
    confidence: float
    is_uncertain: bool
    requires_manual_inspection: bool
    uncertainty_reason: Optional[str]
    raw_probabilities: Dict[str, float] = field(default_factory=dict)
    model_version: str = "v1.0"
    threshold_used: float = 0.50
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseMaterialClassifier(ABC):
    """Abstract base class for material classification models."""

    @abstractmethod
    def predict(self, image: Image.Image) -> PredictionResult:
        """Executes inference and returns a standardized PredictionResult."""
        pass


class BaseDefectDetector(ABC):
    """Abstract base class for whole-image defect detection models."""

    @abstractmethod
    def predict(self, image: Image.Image, threshold: Optional[float] = None) -> PredictionResult:
        """Executes defect inference with configurable confidence threshold."""
        pass
