import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict, field_validator


class AnalysisCreate(BaseModel):
    batch_id: Optional[str] = None


class AnalysisOut(BaseModel):
    id: str
    batch_id: Optional[str]
    image_filename: str
    image_path: str
    file_hash: str

    material_prediction: str
    material_confidence: float
    material_model_version: str

    defect_prediction: str
    defect_confidence: float
    defect_model_version: str
    defect_threshold_used: float
    bounding_boxes: Optional[Any] = None

    is_uncertain: bool
    requires_manual_inspection: bool
    uncertainty_reason: Optional[str]

    waste_category: str
    circularity_score: float
    circularity_category: Optional[str] = None
    scoring_breakdown: Optional[Any] = None
    recommendations: Optional[str]
    operator_id: str
    created_at: datetime

    @field_validator("bounding_boxes", mode="before")
    @classmethod
    def parse_bounding_boxes(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return []
        return v or []

    @field_validator("scoring_breakdown", mode="before")
    @classmethod
    def parse_scoring_breakdown(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return None
        return v

    model_config = ConfigDict(from_attributes=True)


class AnalysisDetailOut(AnalysisOut):
    environmental_impact: Optional[Dict[str, Any]] = None
    operator_username: Optional[str] = None
    circularity_breakdown: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)
