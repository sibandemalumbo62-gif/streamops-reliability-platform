from datetime import datetime
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel


class UserPreferenceBase(BaseModel):
    preferred_genres: Optional[List[str]] = None
    preferred_languages: Optional[List[str]] = None
    disliked_genres: Optional[List[str]] = None
    favorite_directors: Optional[List[str]] = None
    favorite_actors: Optional[List[str]] = None
    watch_history_weights: Optional[dict] = None
    rating_preferences: Optional[dict] = None


class UserPreferenceCreate(UserPreferenceBase):
    user_id: UUID


class UserPreferenceUpdate(UserPreferenceBase):
    pass


class UserPreferenceResponse(UserPreferenceBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
