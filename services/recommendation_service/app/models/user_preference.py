import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, JSON, Float
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        index=True
    )

    preferred_genres: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(String(50)),
        nullable=True
    )

    preferred_languages: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(String(50)),
        nullable=True
    )

    disliked_genres: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(String(50)),
        nullable=True
    )

    favorite_directors: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(String(255)),
        nullable=True
    )

    favorite_actors: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(String(255)),
        nullable=True
    )

    watch_history_weights: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True
    )  # genre -> weight based on watch history

    rating_preferences: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True
    )  # min_rating, content_type preferences

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
