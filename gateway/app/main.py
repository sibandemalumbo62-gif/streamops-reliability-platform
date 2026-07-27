
from fastapi import FastAPI, Request, HTTPException  # type: ignore[import]
from starlette.middleware.cors import CORSMiddleware
import time
from collections import defaultdict
import asyncio
from prometheus_fastapi_instrumentator import Instrumentator
from typing import Dict
try:
    import httpx  # type: ignore[import-not-found]
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    httpx = None
try:
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor  # type: ignore
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    FastAPIInstrumentor = None
    HTTPXClientInstrumentor = None

from . import tracing # noqa: F401
from .middleware.rate_limiter import RateLimiterMiddleware
from .middleware.auth import AuthMiddleware
from .routes.proxy import router as proxy_router
from app.core.config import settings
from app.middleware.request_id import RequestIDMiddleware
app = FastAPI(
    title="StreamOps API Gateway",
    version="1.0.0",
    description="API Gateway for StreamOps Reliability Platform"
)
Instrumentator().instrument(app).expose(app)
# Instrumentation (optional)
if FastAPIInstrumentor is not None:
    try:
        FastAPIInstrumentor.instrument_app(app)
    except Exception:
        pass
if HTTPXClientInstrumentor is not None:
    try:
        HTTPXClientInstrumentor().instrument()
    except Exception:
        pass

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware

app.add_middleware(RequestIDMiddleware)
app.add_middleware(AuthMiddleware)
app.add_middleware(RateLimiterMiddleware)

# Service URLs
SERVICE_URLS = {
    "auth": settings.AUTH_SERVICE_URL,
    "catalog": settings.CATALOG_SERVICE_URL,
    "playback": settings.PLAYBACK_SERVICE_URL,
    "recommendation": settings.RECOMMENDATION_SERVICE_URL,
    "notification": settings.NOTIFICATION_SERVICE_URL,
    "integrity": settings.INTEGRITY_SERVICE_URL,
}
# Include routes
app.include_router(proxy_router)


@app.get("/health")
async def health_check():
    if httpx is None:
        raise HTTPException(status_code=500, detail="httpx dependency is not installed")

    services = []

    overall_status = "healthy"

    for service_name, service_url in SERVICE_URLS.items():

        start = time.perf_counter()

        try:

            async with httpx.AsyncClient(timeout=3.0) as client:

                await client.get(f"{service_url}/health")

            latency = round(
                (time.perf_counter() - start) * 1000,
                2
            )

            status = "healthy"

        except Exception:

            latency = 0

            status = "unhealthy"

            overall_status = "degraded"

        services.append({

            "service": service_name,

            "status": status,

            "latency_ms": latency,

            "last_check": time.strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        })

    return {

        "overall_status": overall_status,

        "services": services,

        "uptime": int(time.monotonic()),

        "version": "1.0.0"

    }


@app.get("/")
async def root():
    return {
        "message": "StreamOps API Gateway",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/v1/auth/*",
            "catalog": "/api/v1/catalog/*",
            "playback": "/api/v1/playback/*",
            "recommendation": "/api/v1/recommendations/*",
            "notification": "/api/v1/notifications/*",
            "integrity": "/api/v1/events/*"
        }
    }
