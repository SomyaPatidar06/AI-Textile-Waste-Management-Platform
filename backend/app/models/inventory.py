import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class BatchStatusEnum(str, enum.Enum):
    COLLECTED = "COLLECTED"
    SORTED = "SORTED"
    PROCESSED = "PROCESSED"
    DISPATCHED = "DISPATCHED"


class TextileBatch(Base):
    __tablename__ = "textile_batches"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    batch_code: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    declared_material: Mapped[str] = mapped_column(String(50), nullable=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[BatchStatusEnum] = mapped_column(
        Enum(BatchStatusEnum),
        default=BatchStatusEnum.COLLECTED,
        nullable=False,
        index=True
    )
    location: Mapped[str] = mapped_column(String(100), nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    operator_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    operator = relationship("User", back_populates="batches", foreign_keys=[operator_id])
    status_history = relationship("StatusHistory", back_populates="batch", cascade="all, delete-orphan", order_by="desc(StatusHistory.created_at)")
    analyses = relationship("AnalysisRecord", back_populates="batch")


class StatusHistory(Base):
    __tablename__ = "status_history"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    batch_id: Mapped[str] = mapped_column(String(36), ForeignKey("textile_batches.id"), nullable=False, index=True)
    old_status: Mapped[str] = mapped_column(String(30), nullable=True)
    new_status: Mapped[str] = mapped_column(String(30), nullable=False)
    changed_by_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    notes: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    batch = relationship("TextileBatch", back_populates="status_history")
    changed_by = relationship("User")
