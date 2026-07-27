import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PlaybackSession(Base):
    __tablename__ = "playback_sessions"

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

    content_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True
    )

    session_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="ACTIVE",
        index=True
    )  # ACTIVE, PAUSED, STOPPED, ERROR

    current_position: Mapped[int] = mapped_column(
        Integer,
        default=0
    )  # in seconds

    total_duration: Mapped[int] = mapped_column(
        Integer,
        nullable=True
    )  # in seconds

    quality: Mapped[str] = mapped_column(
        String(50),
        default="AUTO"
    )  # AUTO, 1080p, 720p, 480p, 360p

    bitrate: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )  # in kbps

    buffer_health: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )  # in seconds

    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    last_activity: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    ended_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )

    device_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )  # WEB, MOBILE, TV, etc.

    ip_address: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
