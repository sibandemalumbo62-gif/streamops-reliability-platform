from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from services.auth_service.app.core.config import settings
from services.auth_service.app.db.dependencies import get_db
from services.auth_service.repositories.user_repository import get_user_by_email


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )


    try:

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[
                settings.ALGORITHM
            ]
        )

        email = payload.get("sub")


        if email is None:
            raise credentials_exception


    except JWTError:
        raise credentials_exception



    user = get_user_by_email(
        db,
        email
    )


    if user is None:
        raise credentials_exception


    return user