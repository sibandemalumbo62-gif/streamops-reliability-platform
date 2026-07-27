from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime

from .database import Base


class IncidentEvent(Base):

    __tablename__ = "incident_events"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    alert_id = Column(
        Integer,
        ForeignKey("alerts.id"),
        nullable=False
    )

    event_type = Column(
        String,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )