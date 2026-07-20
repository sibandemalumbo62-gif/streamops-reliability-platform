from datetime import datetime, timedelta, timezone





from jose import jwt
from passlib.context import CryptContext

from services.auth_service.app.core.config import settings


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str):

    print("PASSWORD RECEIVED:", password)
    print("PASSWORD TYPE:", type(password))
    print("PASSWORD LENGTH:", len(password.encode("utf-8")))

    return pwd_context.hash(password)



def verify_password(
    plain_password: str,
    hashed_password: str
):

    return pwd_context.verify(
        plain_password,
        hashed_password
    )



def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update(
        {
            "exp": expire
        }
    )

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )