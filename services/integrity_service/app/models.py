from sqlalchemy import Column, Integer, String, DateTime

from .database import Base


class Event(Base):

    __tablename__ = "events"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    event_id = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )


    event_type = Column(
        String,
        nullable=False
    )


    user_id = Column(
        String,
        nullable=False
    )


    service = Column(
        String,
        nullable=False
    )


    timestamp = Column(
        DateTime,
        nullable=False
    )


    status = Column(
        String,
        nullable=False,
        default="RECEIVED"
    )


    validation_error = Column(
        String,
        nullable=True
    )