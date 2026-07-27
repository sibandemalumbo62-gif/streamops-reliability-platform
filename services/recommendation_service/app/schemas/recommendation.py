from uuid import UUID
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class RecommendationItem(BaseModel):
    content_id: UUID
    title: str
    content_type: str
    genre: Optional[List[str]] = None
    rating: Optional[float] = None
    match_score: float
    reason: str


class RecommendationResponse(BaseModel):
    user_id: UUID
    recommendations: List[RecommendationItem]
    algorithm_used: str
    total_count: int


class WatchHistoryCreate(BaseModel):
    user_id: UUID
    content_id: UUID
    content_type: str
    genre: Optional[str] = None
    watch_duration: int
    total_duration: int
    user_rating: Optional[int] = None


class WatchHistoryResponse(BaseModel):
    id: UUID
    user_id: UUID
    content_id: UUID
    content_type: str
    genre: Optional[str]
    watch_duration: int
    total_duration: int
    completion_percentage: float
    user_rating: Optional[int]
    watched_at: datetime
    is_completed: bool

    class Config:
        from_attributes = True
