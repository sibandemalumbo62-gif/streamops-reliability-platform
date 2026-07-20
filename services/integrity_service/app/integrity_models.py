from sqlalchemy import Column, Integer, String, DateTime, Boolean

from .database import Base


class IntegrityReport(Base):

    __tablename__ = "integrity_reports"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    event_id = Column(
        String,
        nullable=False
    )


    valid = Column(
        Boolean,
        nullable=False
    )


    error_message = Column(
        String,
        nullable=True
    )


    created_at = Column(
        DateTime
    )