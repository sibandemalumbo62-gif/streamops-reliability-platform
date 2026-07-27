from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timedelta
from typing import Optional, List
import secrets

from app.models.session import PlaybackSession


def get_session_by_id(db: Session, session_id: str):
    return (
        db.query(PlaybackSession)
        .filter(PlaybackSession.session_id == session_id)
        .first()
    )


def get_active_sessions_by_user(db: Session, user_id: str):
    return (
        db.query(PlaybackSession)
        .filter(
            PlaybackSession.user_id == UUID(user_id),
            PlaybackSession.status == "ACTIVE"
        )
        .all()
    )


def create_session(db: Session, session_data: dict):
    session_id = secrets.token_urlsafe(16)
    new_session = PlaybackSession(
        session_id=session_id,
        **session_data
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session


def update_session(db: Session, session_id: str, session_data: dict):
    session = get_session_by_id(db, session_id)
    if not session:
        return None
    
    for key, value in session_data.items():
        setattr(session, key, value)
    
    session.last_activity = datetime.utcnow()
    db.commit()
    db.refresh(session)
    return session


def end_session(db: Session, session_id: str, status: str = "STOPPED"):
    session = get_session_by_id(db, session_id)
    if not session:
        return None
    
    session.status = status
    session.ended_at = datetime.utcnow()
    session.last_activity = datetime.utcnow()
    db.commit()
    db.refresh(session)
    return session


def cleanup_expired_sessions(db: Session, timeout_minutes: int = 120):
    cutoff_time = datetime.utcnow() - timedelta(minutes=timeout_minutes)
    
    expired_sessions = (
        db.query(PlaybackSession)
        .filter(
            PlaybackSession.status == "ACTIVE",
            PlaybackSession.last_activity < cutoff_time
        )
        .all()
    )
    
    for session in expired_sessions:
        session.status = "TIMEOUT"
        session.ended_at = datetime.utcnow()
    
    db.commit()
    return len(expired_sessions)


def get_user_active_session_count(db: Session, user_id: str):
    return (
        db.query(PlaybackSession)
        .filter(
            PlaybackSession.user_id == UUID(user_id),
            PlaybackSession.status == "ACTIVE"
        )
        .count()
    )


def get_session_metrics(db: Session):
    total_active = (
        db.query(PlaybackSession)
        .filter(PlaybackSession.status == "ACTIVE")
        .count()
    )
    
    total_completed = (
        db.query(PlaybackSession)
        .filter(PlaybackSession.status == "STOPPED")
        .count()
    )
    
    # Calculate average session duration
    completed_sessions = (
        db.query(PlaybackSession)
        .filter(
            PlaybackSession.status == "STOPPED",
            PlaybackSession.ended_at.isnot(None)
        )
        .all()
    )
    
    total_duration = 0
    for session in completed_sessions:
        if session.started_at and session.ended_at:
            duration = (session.ended_at - session.started_at).total_seconds()
            total_duration += duration
    
    avg_duration = total_duration / len(completed_sessions) if completed_sessions else 0
    
    return {
        "total_active_sessions": total_active,
        "total_completed_sessions": total_completed,
        "average_session_duration": avg_duration,
        "total_bytes_streamed": 0  # Would be tracked in production
    }
