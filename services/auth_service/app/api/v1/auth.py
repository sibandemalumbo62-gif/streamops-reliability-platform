from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.dependencies import get_db
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
    TokenResponse,
    PasswordResetRequest,
    PasswordResetConfirm
)

from app.services.auth_service import (
    authenticate_user,
    create_user,
    update_user,
    request_password_reset,
    confirm_password_reset
)

from app.core.security import (
    create_access_token
)

from app.core.config import settings


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    try:
        new_user = create_user(db, user)
        return new_user

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        print("REGISTER ERROR:", error)

        raise HTTPException(
            status_code=500,
            detail=f"Registration failed: {str(error)}"
        )


@router.post("/login", response_model=TokenResponse)
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):

    try:
        authenticated_user = authenticate_user(
            db,
            user.email,
            user.password
        )

        if not authenticated_user:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )

        # Update last login
        authenticated_user.last_login = datetime.utcnow()
        db.commit()

        token = create_access_token({"sub": authenticated_user.email})

        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

    except HTTPException:
        raise

    except Exception as error:
        print("LOGIN ERROR:", error)

        raise HTTPException(
            status_code=500,
            detail=f"Login failed: {str(error)}"
        )


@router.post("/password-reset/request")
def request_password_reset_endpoint(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    try:
        reset_token = request_password_reset(db, request.email)
        if reset_token:
            return {"message": "Password reset token sent", "token": reset_token}
        return {"message": "If email exists, reset token sent"}
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Password reset request failed: {str(error)}"
        )


@router.post("/password-reset/confirm")
def confirm_password_reset_endpoint(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    try:
        success = confirm_password_reset(db, request.token, request.new_password)
        if success:
            return {"message": "Password reset successful"}
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset token"
        )
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Password reset failed: {str(error)}"
        )