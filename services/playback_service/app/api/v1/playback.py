from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.dependencies import get_db
from app.schemas.session import (
    PlaybackSessionCreate,
    PlaybackSessionUpdate,
    PlaybackSessionResponse,
    StreamUrlResponse
)
from app.repositories.session_repository import (
    create_session,
    update_session,
    end_session,
    get_user_active_session_count
)
from app.core.config import settings


router = APIRouter(
    prefix="/playback",
    tags=["Playback"],
)


@router.post("/start", response_model=PlaybackSessionResponse)
def start_playback(
    session_data: PlaybackSessionCreate,
    db: Session = Depends(get_db)
):
    try:
        # Check concurrent stream limit
        active_count = get_user_active_session_count(db, str(session_data.user_id))
        if active_count >= settings.MAX_CONCURRENT_STREAMS:
            raise HTTPException(
                status_code=429,
                detail=f"Maximum concurrent streams ({settings.MAX_CONCURRENT_STREAMS}) exceeded"
            )
        
        new_session = create_session(db, session_data.model_dump())
        return new_session
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start playback: {str(error)}"
        )


@router.post("/{session_id}/stream-url", response_model=StreamUrlResponse)
def get_stream_url(
    session_id: str,
    db: Session = Depends(get_db)
):
    try:
        # In production, this would generate a signed URL with expiration
        stream_url = f"https://stream.streamops.io/{session_id}/master.m3u8"
        return {
            "stream_url": stream_url,
            "session_id": session_id,
            "expires_in": settings.STREAM_TIMEOUT_MINUTES * 60,
            "quality": "AUTO"
        }
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate stream URL: {str(error)}"
        )


@router.patch("/{session_id}", response_model=PlaybackSessionResponse)
def update_playback(
    session_id: str,
    session_update: PlaybackSessionUpdate,
    db: Session = Depends(get_db)
):
    try:
        updated_session = update_session(
            db,
            session_id,
            session_update.model_dump(exclude_unset=True)
        )
        if not updated_session:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )
        return updated_session
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update playback: {str(error)}"
        )


@router.post("/{session_id}/pause", response_model=PlaybackSessionResponse)
def pause_playback(
    session_id: str,
    db: Session = Depends(get_db)
):
    try:
        updated_session = update_session(db, session_id, {"status": "PAUSED"})
        if not updated_session:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )
        return updated_session
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to pause playback: {str(error)}"
        )


@router.post("/{session_id}/resume", response_model=PlaybackSessionResponse)
def resume_playback(
    session_id: str,
    db: Session = Depends(get_db)
):
    try:
        updated_session = update_session(db, session_id, {"status": "ACTIVE"})
        if not updated_session:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )
        return updated_session
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to resume playback: {str(error)}"
        )


@router.post("/{session_id}/stop", response_model=PlaybackSessionResponse)
def stop_playback(
    session_id: str,
    db: Session = Depends(get_db)
):
    try:
        ended_session = end_session(db, session_id, "STOPPED")
        if not ended_session:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )
        return ended_session
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to stop playback: {str(error)}"
        )
