from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from repositories.user_repository import (
    get_user_by_email,
    get_user_by_id,
)

from app.core.security import (
    hash_password,
    verify_password,
)


# Simple in-memory token storage (in production, use Redis or database)
reset_tokens = {}


def create_user(
    db: Session,
    user: UserCreate
):
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise ValueError("Email already registered")

    new_user = User(
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        hashed_password=hash_password(user.password),
    )


    db.add(new_user)

    db.commit()

    db.refresh(new_user)
    
    return new_user



def authenticate_user(
    db: Session,
    email: str,
    password: str,
):
    user = get_user_by_email(db, email)
    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


def update_user(
    db: Session,
    user_id: str,
    user_update: UserUpdate,
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise ValueError("User not found")

    if user_update.first_name is not None:
        user.first_name = user_update.first_name
    if user_update.last_name is not None:
        user.last_name = user_update.last_name
    if user_update.username is not None:
        user.username = user_update.username

    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user


def request_password_reset(
    db: Session,
    email: str,
):
    user = get_user_by_email(db, email)
    if not user:
        return None

    token = secrets.token_urlsafe(32)

    reset_tokens[token] = {
        "user_id": str(user.id),
        "expires_at": datetime.utcnow() + timedelta(hours=1),
    }

    return token


def confirm_password_reset(
    db: Session,
    token: str,
    new_password: str,
):
    if token not in reset_tokens:
        return False

    token_data = reset_tokens[token]

    if datetime.utcnow() > token_data["expires_at"]:
        del reset_tokens[token]
        return False

    user = get_user_by_id(db, token_data["user_id"])

    if not user:
        del reset_tokens[token]
        return False

    user.hashed_password = hash_password(new_password)
    user.updated_at = datetime.utcnow()

    db.commit()

    del reset_tokens[token]

    return True