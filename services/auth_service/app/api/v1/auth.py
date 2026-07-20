from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from services.auth_service.app.db.dependencies import get_db
from services.auth_service.app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse
)

from services.auth_service.app.services.auth_service import (
    authenticate_user,
    create_user
)

from services.auth_service.app.core.security import (
    create_access_token
)


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
        new_user = create_user(
            db,
            user
        )

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


@router.post("/login")
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


        token = create_access_token(
            {
                "sub": authenticated_user.email
            }
        )


        return {
            "access_token": token,
            "token_type": "bearer"
        }

    except HTTPException:
        raise

    except Exception as error:
        print("LOGIN ERROR:", error)

        raise HTTPException(
            status_code=500,
            detail=f"Login failed: {str(error)}"
        )