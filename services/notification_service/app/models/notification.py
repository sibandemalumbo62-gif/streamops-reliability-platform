import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Boolean, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True
    )

    notification_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # EMAIL, PUSH, IN_APP

    channel: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )  # MARKETING, TRANSACTIONAL, ALERT

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    body: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    data: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="PENDING",
        index=True
    )  # PENDING, SENT, FAILED, DELIVERED

    priority: Mapped[str] = mapped_column(
        String(50),
        default="NORMAL"
    )  # LOW, NORMAL, HIGH, URGENT

    scheduled_for: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )

    sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )

    delivered_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    retry_count: Mapped[int] = mapped_column(
        default=0
    )

    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        index=True
    )

    template_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True
    )
