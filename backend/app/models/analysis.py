import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class AnalysisRecord(Base):
    __tablename__ = "analysis_records"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    batch_id: Mapped[str] = mapped_column(String(36), ForeignKey("textile_batches.id"), nullable=True, index=True)
    image_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    image_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # Material classification fields (Visual Estimates)
    material_prediction: Mapped[str] = mapped_column(String(50), nullable=False)
    material_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    material_model_version: Mapped[str] = mapped_column(String(50), nullable=False)

    # Defect classification fields
    defect_prediction: Mapped[str] = mapped_column(String(50), nullable=False)
    defect_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    defect_model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    defect_threshold_used: Mapped[float] = mapped_column(Float, nullable=False)
    bounding_boxes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Uncertainty & Governance
    is_uncertain: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_manual_inspection: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    uncertainty_reason: Mapped[str] = mapped_column(String(255), nullable=True)

    # Circularity & Decision outputs
    waste_category: Mapped[str] = mapped_column(String(50), nullable=False)
    circularity_score: Mapped[float] = mapped_column(Float, nullable=False)
    circularity_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    scoring_breakdown: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recommendations: Mapped[str] = mapped_column(Text, nullable=True)

    operator_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    batch = relationship("TextileBatch", back_populates="analyses")
    operator = relationship("User", back_populates="analyses", foreign_keys=[operator_id])
