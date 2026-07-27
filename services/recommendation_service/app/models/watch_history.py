import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Integer, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class WatchHistory(Base):
    __tablename__ = "watch_history"

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

    content_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    genre: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    watch_duration: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )  # in seconds

    total_duration: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )  # in seconds

    completion_percentage: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    user_rating: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )  # 1-5 stars

    watched_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        index=True
    )

    is_completed: Mapped[bool] = mapped_column(
        default=False
    )
