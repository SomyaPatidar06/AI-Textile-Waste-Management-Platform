from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.models.inventory import BatchStatusEnum


class BatchCreate(BaseModel):
    batch_code: str
    weight_kg: float
    declared_material: Optional[str] = None
    source_type: str
    location: Optional[str] = None
    notes: Optional[str] = None


class BatchUpdate(BaseModel):
    weight_kg: Optional[float] = None
    declared_material: Optional[str] = None
    source_type: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None


class BatchStatusUpdate(BaseModel):
    status: BatchStatusEnum
    notes: Optional[str] = None


class StatusHistoryOut(BaseModel):
    id: str
    batch_id: str
    old_status: Optional[str]
    new_status: str
    changed_by_id: str
    notes: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BatchOut(BaseModel):
    id: str
    batch_code: str
    weight_kg: float
    declared_material: Optional[str]
    source_type: str
    status: BatchStatusEnum
    location: Optional[str]
    notes: Optional[str]
    operator_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BatchDetailOut(BatchOut):
    status_history: List[StatusHistoryOut] = []

    model_config = ConfigDict(from_attributes=True)
