from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.notification import NotificationCategoryEnum


class NotificationCreate(BaseModel):
    user_id: str
    title: str
    message: str
    category: NotificationCategoryEnum = NotificationCategoryEnum.SYSTEM


class NotificationOut(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    category: NotificationCategoryEnum
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
