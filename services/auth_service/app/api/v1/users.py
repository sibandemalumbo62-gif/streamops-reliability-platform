from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.dependencies import get_db
from app.schemas.user import (
    UserResponse,
    UserUpdate
)
from app.services.auth_service import update_user
from repositories.user_repository import get_user_by_id


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return user


@router.patch("/{user_id}", response_model=UserResponse)
def update_user_endpoint(
    user_id: str,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    try:
        updated_user = update_user(db, user_id, user_update)
        return updated_user
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"User update failed: {str(error)}"
        )
