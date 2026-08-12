from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, Text


from ..database import Base


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String(30), nullable=False, default="healthy")
    created_at = Column(DateTime, default=datetime.utcnow)


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(100), unique=True, nullable=False, index=True)
    event_type = Column(String(100), nullable=False)
    service = Column(String(100), nullable=False, index=True)
    processing_latency_ms = Column(Float, nullable=True)
    status = Column(String(30), nullable=False, default="processed")
    created_at = Column(DateTime, default=datetime.utcnow)


class ReliabilityMetric(Base):
    __tablename__ = "reliability_metrics"

    id = Column(Integer, primary_key=True, index=True)

    service = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    availability = Column(Float, default=100.0)

    success_rate = Column(Float, default=100.0)

    error_rate = Column(Float, default=0.0)

    latency_ms = Column(Float, default=0.0)

    throughput = Column(Float, default=0.0)

    consumer_lag_seconds = Column(Float, default=0.0)

    reliability_score = Column(Float, default=100.0)

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
class SLO(Base):
    __tablename__ = "slos"

    id = Column(Integer, primary_key=True, index=True)
    service = Column(String(100), nullable=False, index=True)
    name = Column(String(150), nullable=False)

    target = Column(Float, nullable=False)
    current_value = Column(Float, default=100.0)
    error_budget_remaining = Column(Float, default=100.0)
    status = Column(String(30), default="meeting")

    created_at = Column(DateTime, default=datetime.utcnow)


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_number = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    service = Column(String(100), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    severity = Column(String(30), default="medium")
    status = Column(String(30), default="open")

    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
