from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from .database import Base


class Job(Base):

    __tablename__ = "jobs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    job_type = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        default="PENDING"
    )

    progress = Column(
        Integer,
        default=0
    )

    requested_by = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    completed_at = Column(
        DateTime,
        nullable=True
    )