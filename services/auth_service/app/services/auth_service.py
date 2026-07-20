from sqlalchemy.orm import Session

from services.auth_service.app.models.user import User
from services.auth_service.app.schemas.user import UserCreate
from services.auth_service.repositories.user_repository import (
    get_user_by_email
)

from services.auth_service.app.core.security import (
    hash_password,
    verify_password
)


def create_user(
    db: Session,
    user: UserCreate
):

    existing_user = get_user_by_email(
        db,
        user.email
    )

    if existing_user:
        raise ValueError(
            "Email already registered"
        )


    new_user = User(
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        hashed_password=hash_password(
            user.password
        )
    )


    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return new_user



def authenticate_user(
    db: Session,
    email: str,
    password: str
):

    user = get_user_by_email(
        db,
        email
    )

    if not user:
        return None


    if not verify_password(
        password,
        user.hashed_password
    ):
        return None


    return user