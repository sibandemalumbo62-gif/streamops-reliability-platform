
from fastapi import FastAPI  # type: ignore[import-not-found]
from app.api.v1.recommendations import router as recommendations_router
from app.api.v1.preferences import router as preferences_router
from prometheus_fastapi_instrumentator import Instrumentator
app = FastAPI(
    title="StreamOps Recommendation Service",
    version="1.0.0",
    description="Recommendation engine microservice for StreamOps Reliability Platform"
)
Instrumentator().instrument(app).expose(app)
app.include_router(recommendations_router)
app.include_router(preferences_router)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "recommendation-service"
    }
