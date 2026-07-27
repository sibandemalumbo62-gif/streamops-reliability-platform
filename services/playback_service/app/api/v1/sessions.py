from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.dependencies import get_db
from app.schemas.session import PlaybackSessionResponse, PlaybackMetrics
from app.repositories.session_repository import (
    get_session_by_id,
    get_active_sessions_by_user,
    get_session_metrics,
    cleanup_expired_sessions
)


router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"],
)


@router.get("/{session_id}", response_model=PlaybackSessionResponse)
def get_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    session = get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )
    return session


@router.get("/user/{user_id}/active", response_model=List[PlaybackSessionResponse])
def get_user_active_sessions(
    user_id: str,
    db: Session = Depends(get_db)
):
    try:
        sessions = get_active_sessions_by_user(db, user_id)
        return sessions
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch sessions: {str(error)}"
        )


@router.get("/metrics", response_model=PlaybackMetrics)
def get_playback_metrics(
    db: Session = Depends(get_db)
):
    try:
        metrics = get_session_metrics(db)
        return metrics
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch metrics: {str(error)}"
        )


@router.post("/cleanup")
def cleanup_sessions(
    db: Session = Depends(get_db)
):
    try:
        cleaned_count = cleanup_expired_sessions(db)
        return {
            "message": f"Cleaned up {cleaned_count} expired sessions",
            "cleaned_count": cleaned_count
        }
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cleanup sessions: {str(error)}"
        )
