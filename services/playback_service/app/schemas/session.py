from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field


class PlaybackSessionCreate(BaseModel):
    user_id: UUID
    content_id: UUID
    quality: str = "AUTO"
    device_type: Optional[str] = None
    ip_address: Optional[str] = None


class PlaybackSessionUpdate(BaseModel):
    current_position: Optional[int] = None
    status: Optional[str] = None
    quality: Optional[str] = None
    bitrate: Optional[int] = None
    buffer_health: Optional[float] = None


class PlaybackSessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    content_id: UUID
    session_id: str
    status: str
    current_position: int
    total_duration: Optional[int]
    quality: str
    bitrate: Optional[int]
    buffer_health: Optional[float]
    started_at: datetime
    last_activity: datetime
    ended_at: Optional[datetime]
    error_message: Optional[str]
    device_type: Optional[str]
    ip_address: Optional[str]

    class Config:
        from_attributes = True


class StreamUrlResponse(BaseModel):
    stream_url: str
    session_id: str
    expires_in: int
    quality: str


class PlaybackMetrics(BaseModel):
    total_active_sessions: int
    total_completed_sessions: int
    average_session_duration: float
    total_bytes_streamed: int
