from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from typing import List, Optional

from app.models.notification import Notification
from app.models.template import NotificationTemplate


def create_notification(db: Session, notification_data: dict):
    new_notification = Notification(**notification_data)
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)
    return new_notification


def get_notification_by_id(db: Session, notification_id: str):
    return (
        db.query(Notification)
        .filter(Notification.id == UUID(notification_id))
        .first()
    )


def get_user_notifications(
    db: Session,
    user_id: str,
    skip: int = 0,
    limit: int = 50,
    unread_only: bool = False
):
    query = db.query(Notification).filter(Notification.user_id == UUID(user_id))
    
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    return (
        query
        .order_by(Notification.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_notification(db: Session, notification_id: str, notification_data: dict):
    notification = get_notification_by_id(db, notification_id)
    if not notification:
        return None
    
    for key, value in notification_data.items():
        setattr(notification, key, value)
    
    if notification_data.get("is_read") and not notification.read_at:
        notification.read_at = datetime.utcnow()
    
    db.commit()
    db.refresh(notification)
    return notification


def mark_as_read(db: Session, notification_id: str):
    return update_notification(
        db,
        notification_id,
        {"is_read": True}
    )


def mark_all_as_read(db: Session, user_id: str):
    notifications = (
        db.query(Notification)
        .filter(
            Notification.user_id == UUID(user_id),
            Notification.is_read == False
        )
        .all()
    )
    
    for notification in notifications:
        notification.is_read = True
        notification.read_at = datetime.utcnow()
    
    db.commit()
    return len(notifications)


def get_pending_notifications(db: Session, limit: int = 100):
    return (
        db.query(Notification)
        .filter(
            Notification.status == "PENDING",
            (Notification.scheduled_for.is_(None)) | 
            (Notification.scheduled_for <= datetime.utcnow())
        )
        .order_by(Notification.priority.desc(), Notification.created_at.asc())
        .limit(limit)
        .all()
    )


def update_notification_status(
    db: Session,
    notification_id: str,
    status: str,
    error_message: Optional[str] = None
):
    notification = get_notification_by_id(db, notification_id)
    if not notification:
        return None
    
    notification.status = status
    
    if status == "SENT":
        notification.sent_at = datetime.utcnow()
    elif status == "DELIVERED":
        notification.delivered_at = datetime.utcnow()
    elif status == "FAILED":
        notification.retry_count += 1
        notification.error_message = error_message
    
    db.commit()
    db.refresh(notification)
    return notification
