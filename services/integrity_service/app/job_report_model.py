from sqlalchemy import Column, Integer, Float, DateTime
from datetime import datetime

from .database import Base


class JobReport(Base):

    __tablename__ = "job_reports"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    job_id = Column(
        Integer,
        nullable=False
    )

    total_events = Column(
        Integer,
        default=0
    )

    accepted_events = Column(
        Integer,
        default=0
    )

    rejected_events = Column(
        Integer,
        default=0
    )

    success_rate = Column(
        Float,
        default=0
    )

    failure_rate = Column(
        Float,
        default=0
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )