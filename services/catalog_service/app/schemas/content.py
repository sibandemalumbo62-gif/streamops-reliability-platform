from datetime import datetime
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, Field


class ContentBase(BaseModel):
    title: str
    description: Optional[str] = None
    content_type: str
    genre: Optional[List[str]] = None
    duration: Optional[int] = None
    release_year: Optional[int] = None
    rating: Optional[float] = None
    language: Optional[str] = None
    director: Optional[str] = None
    cast: Optional[List[str]] = None
    thumbnail_url: Optional[str] = None
    video_url: Optional[str] = None
    metadata: Optional[dict] = None


class ContentCreate(ContentBase):
    pass


class ContentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content_type: Optional[str] = None
    genre: Optional[List[str]] = None
    duration: Optional[int] = None
    release_year: Optional[int] = None
    rating: Optional[float] = None
    language: Optional[str] = None
    director: Optional[str] = None
    cast: Optional[List[str]] = None
    thumbnail_url: Optional[str] = None
    video_url: Optional[str] = None
    metadata: Optional[dict] = None
    is_available: Optional[bool] = None


class ContentResponse(ContentBase):
    id: UUID
    is_available: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContentSearchResponse(BaseModel):
    count: int
    results: List[ContentResponse]
