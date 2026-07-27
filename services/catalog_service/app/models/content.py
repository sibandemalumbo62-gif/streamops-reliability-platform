import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, Integer, Float, DateTime, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Content(Base):
    __tablename__ = "content"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    content_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # MOVIE, SERIES, DOCUMENTARY, etc.

    genre: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(String(50)),
        nullable=True
    )

    duration: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )  # in minutes

    release_year: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )

    rating: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )  # 0.0 to 10.0

    language: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    director: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    cast: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(String(255)),
        nullable=True
    )

    thumbnail_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )

    video_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )

    content_metadata: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True
    )

    is_available: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
