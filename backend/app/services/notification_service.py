from typing import Optional
from sqlalchemy.orm import Session
from app.models.notification import Notification, NotificationCategoryEnum
from app.models.user import User, RoleEnum


def create_notification(
    db: Session,
    user_id: str,
    title: str,
    message: str,
    category: NotificationCategoryEnum = NotificationCategoryEnum.SYSTEM
) -> Notification:
    """Creates a persistent in-app notification for a designated user."""
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        category=category,
        is_read=False
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def notify_admins(
    db: Session,
    title: str,
    message: str,
    category: NotificationCategoryEnum = NotificationCategoryEnum.SYSTEM
) -> None:
    """Broadcasts an in-app notification to all active system administrators."""
    admins = db.query(User).filter(
        User.role == RoleEnum.ADMIN,
        User.is_active == True
    ).all()
    for admin in admins:
        create_notification(db, admin.id, title, message, category)
