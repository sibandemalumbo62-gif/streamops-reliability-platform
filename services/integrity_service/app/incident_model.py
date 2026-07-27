from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from .database import Base


class Incident(Base):

    __tablename__ = "incidents"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    service = Column(
        String,
        nullable=False
    )


    severity = Column(
        String,
        nullable=False
    )


    message = Column(
        String,
        nullable=False
    )


    status = Column(
        String,
        default="OPEN"
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
    resolved_at = Column(
    DateTime,
    nullable=True
)