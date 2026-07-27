
from fastapi import FastAPI  # type: ignore[import]
from app.api.v1.notifications import router as notifications_router
from app.api.v1.templates import router as templates_router
from prometheus_fastapi_instrumentator import Instrumentator
app = FastAPI(
    title="StreamOps Notification Service",
    version="1.0.0",
    description="Notification microservice for StreamOps Reliability Platform"
)
Instrumentator().instrument(app).expose(app)
app.include_router(notifications_router)
app.include_router(templates_router)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "notification-service"
    }
