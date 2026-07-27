from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.dependencies import get_db
from app.schemas.preference import (
    UserPreferenceCreate,
    UserPreferenceUpdate,
    UserPreferenceResponse
)
from app.repositories.preference_repository import (
    get_user_preference,
    create_user_preference,
    update_user_preference
)


router = APIRouter(
    prefix="/preferences",
    tags=["Preferences"],
)


@router.get("/{user_id}", response_model=UserPreferenceResponse)
def get_user_preferences(
    user_id: str,
    db: Session = Depends(get_db)
):
    preference = get_user_preference(db, user_id)
    if not preference:
        raise HTTPException(
            status_code=404,
            detail="User preferences not found"
        )
    return preference


@router.post("/", response_model=UserPreferenceResponse, status_code=201)
def create_user_preferences(
    preference: UserPreferenceCreate,
    db: Session = Depends(get_db)
):
    try:
        # Check if preferences already exist
        existing = get_user_preference(db, str(preference.user_id))
        if existing:
            raise HTTPException(
                status_code=400,
                detail="User preferences already exist"
            )
        
        new_preference = create_user_preference(db, preference.model_dump())
        return new_preference
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create preferences: {str(error)}"
        )


@router.patch("/{user_id}", response_model=UserPreferenceResponse)
def update_user_preferences(
    user_id: str,
    preference_update: UserPreferenceUpdate,
    db: Session = Depends(get_db)
):
    try:
        updated_preference = update_user_preference(
            db,
            user_id,
            preference_update.model_dump(exclude_unset=True)
        )
        if not updated_preference:
            raise HTTPException(
                status_code=404,
                detail="User preferences not found"
            )
        return updated_preference
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update preferences: {str(error)}"
        )
