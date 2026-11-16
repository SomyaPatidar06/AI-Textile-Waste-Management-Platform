import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class NotificationCategoryEnum(str, enum.Enum):
    SYSTEM = "SYSTEM"
    BATCH = "BATCH"
    INSPECTION = "INSPECTION"
    CIRCULARITY = "CIRCULARITY"


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[NotificationCategoryEnum] = mapped_column(
        Enum(NotificationCategoryEnum),
        default=NotificationCategoryEnum.SYSTEM,
        nullable=False
    )
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", back_populates="notifications")
