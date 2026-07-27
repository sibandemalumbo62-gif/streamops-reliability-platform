from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel


class NotificationCreate(BaseModel):
    user_id: UUID
    notification_type: str  # EMAIL, PUSH, IN_APP
    channel: str  # MARKETING, TRANSACTIONAL, ALERT
    title: str
    body: str
    data: Optional[dict] = None
    priority: str = "NORMAL"
    scheduled_for: Optional[datetime] = None
    template_id: Optional[UUID] = None


class NotificationUpdate(BaseModel):
    status: Optional[str] = None
    is_read: Optional[bool] = None


class NotificationResponse(BaseModel):
    id: UUID
    user_id: UUID
    notification_type: str
    channel: str
    title: str
    body: str
    data: Optional[dict]
    status: str
    priority: str
    scheduled_for: Optional[datetime]
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    error_message: Optional[str]
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class BulkNotificationCreate(BaseModel):
    user_ids: list[UUID]
    notification_type: str
    channel: str
    title: str
    body: str
    data: Optional[dict] = None
    priority: str = "NORMAL"
