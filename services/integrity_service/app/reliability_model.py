from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from .database import Base


class ReliabilityMetric(Base):

    __tablename__ = "reliability_metrics"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    service = Column(
        String,
        nullable=False,
        unique=True
    )

    total_events = Column(
        Integer,
        default=0
    )

    rejected_events = Column(
        Integer,
        default=0
    )

    reliability_score = Column(
        Float,
        default=100.0
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )