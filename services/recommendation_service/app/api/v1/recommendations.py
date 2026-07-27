from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.db.dependencies import get_db
from app.schemas.recommendation import (
    RecommendationResponse,
    RecommendationItem,
    WatchHistoryCreate,
    WatchHistoryResponse
)
from app.repositories.preference_repository import (
    get_user_preference,
    add_watch_history,
    get_user_watch_history,
    get_user_genre_preferences
)
from app.services.recommendation_engine import recommendation_engine
from app.core.config import settings


router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"],
)


@router.get("/{user_id}", response_model=RecommendationResponse)
def get_recommendations(
    user_id: str,
    limit: int = Query(settings.RECOMMENDATION_COUNT, ge=1, le=50),
    db: Session = Depends(get_db)
):
    try:
        # Get user preferences
        user_pref = get_user_preference(db, user_id)
        if not user_pref:
            # Return default recommendations for new users
            return {
                "user_id": UUID(user_id),
                "recommendations": [],
                "algorithm_used": "default",
                "total_count": 0
            }
        
        # Get watch history
        watch_history = get_user_watch_history(db, user_id)
        
        # Update genre weights based on watch history
        genre_weights = get_user_genre_preferences(db, user_id)
        if genre_weights:
            user_pref.watch_history_weights = genre_weights
        
        # Mock available content (in production, this would come from catalog service)
        available_content = _get_mock_content()
        
        # Generate recommendations
        recommendations = recommendation_engine.generate_recommendations(
            user_pref.model_dump(),
            watch_history,
            available_content,
            limit
        )
        
        recommendation_items = [
            RecommendationItem(**rec) for rec in recommendations
        ]
        
        return {
            "user_id": UUID(user_id),
            "recommendations": recommendation_items,
            "algorithm_used": recommendation_engine.algorithm,
            "total_count": len(recommendation_items)
        }
        
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(error)}"
        )


@router.post("/watch-history", response_model=WatchHistoryResponse)
def add_watch_history_endpoint(
    history: WatchHistoryCreate,
    db: Session = Depends(get_db)
):
    try:
        new_history = add_watch_history(db, history.model_dump())
        return new_history
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add watch history: {str(error)}"
        )


@router.get("/{user_id}/watch-history", response_model=List[WatchHistoryResponse])
def get_user_history(
    user_id: str,
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db)
):
    try:
        history = get_user_watch_history(db, user_id, limit)
        return history
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch watch history: {str(error)}"
        )


def _get_mock_content() -> List[dict]:
    """
    Mock content data - in production, this would be fetched from catalog service
    """
    return [
        {
            "id": UUID("123e4567-e89b-12d3-a456-426614174000"),
            "title": "The Matrix",
            "content_type": "MOVIE",
            "genre": ["Sci-Fi", "Action"],
            "rating": 8.7,
            "director": "Wachowskis",
            "language": "English"
        },
        {
            "id": UUID("123e4567-e89b-12d3-a456-426614174001"),
            "title": "Inception",
            "content_type": "MOVIE",
            "genre": ["Sci-Fi", "Thriller"],
            "rating": 8.8,
            "director": "Christopher Nolan",
            "language": "English"
        },
        {
            "id": UUID("123e4567-e89b-12d3-a456-426614174002"),
            "title": "Breaking Bad",
            "content_type": "SERIES",
            "genre": ["Drama", "Crime"],
            "rating": 9.5,
            "director": "Vince Gilligan",
            "language": "English"
        }
    ]
