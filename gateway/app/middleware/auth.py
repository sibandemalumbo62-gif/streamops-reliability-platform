from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from jose import jwt, JWTError

from typing import List
from app.core.config import settings
PUBLIC_PATHS = [
    "/docs",
    "/openapi.json",
    "/redoc",
    "/health",
    "/metrics"
]


class AuthMiddleware(BaseHTTPMiddleware):

    PUBLIC_ROUTES: List[str] = [
        "/health",
        
        "/api/v1/auth/register",
        "/api/v1/auth/login",
        "/api/v1/auth/password-reset",
    ]


    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        print("AUTH MIDDLEWARE HIT:", path)

        # Allow public endpoints
        if any(path.startswith(route) for route in self.PUBLIC_ROUTES) or path in PUBLIC_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")

        print("=" * 50)
        print("PATH:", request.url.path)
        print("AUTH HEADER:", auth_header)
        print("HEADERS:", dict(request.headers))
        print("=" * 50)
        if not auth_header:
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Unauthorized",
                    "message": "Missing authorization header"
                }
            )

        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Unauthorized",
                    "message": "Invalid authorization format"
                }
            )

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )

            user_email = payload.get("sub")

            if not user_email:
                raise JWTError()

            request.state.user_id = user_email

        except JWTError:
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Unauthorized",
                    "message": "Invalid or expired token"
                }
            )

        return await call_next(request)