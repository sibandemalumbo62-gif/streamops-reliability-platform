from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List

from app.models.user_preference import UserPreference
from app.models.watch_history import WatchHistory


def get_user_preference(db: Session, user_id: str):
    return (
        db.query(UserPreference)
        .filter(UserPreference.user_id == UUID(user_id))
        .first()
    )


def create_user_preference(db: Session, preference_data: dict):
    new_preference = UserPreference(**preference_data)
    db.add(new_preference)
    db.commit()
    db.refresh(new_preference)
    return new_preference


def update_user_preference(db: Session, user_id: str, preference_data: dict):
    preference = get_user_preference(db, user_id)
    if not preference:
        return None
    
    for key, value in preference_data.items():
        setattr(preference, key, value)
    
    db.commit()
    db.refresh(preference)
    return preference


def add_watch_history(db: Session, history_data: dict):
    completion_percentage = (
        (history_data["watch_duration"] / history_data["total_duration"]) * 100
        if history_data["total_duration"] > 0
        else 0
    )
    
    history_data["completion_percentage"] = completion_percentage
    history_data["is_completed"] = completion_percentage >= 90
    
    new_history = WatchHistory(**history_data)
    db.add(new_history)
    db.commit()
    db.refresh(new_history)
    return new_history


def get_user_watch_history(db: Session, user_id: str, limit: int = 100):
    return (
        db.query(WatchHistory)
        .filter(WatchHistory.user_id == UUID(user_id))
        .order_by(WatchHistory.watched_at.desc())
        .limit(limit)
        .all()
    )


def get_user_genre_preferences(db: Session, user_id: str):
    history = get_user_watch_history(db, user_id, limit=50)
    
    genre_counts = {}
    for item in history:
        if item.genre:
            genre_counts[item.genre] = genre_counts.get(item.genre, 0) + 1
    
    # Normalize to weights
    total = sum(genre_counts.values())
    if total > 0:
        genre_weights = {
            genre: count / total 
            for genre, count in genre_counts.items()
        }
    else:
        genre_weights = {}
    
    return genre_weights
