
# pyright: reportMissingImports=false
from fastapi import FastAPI
from app.api.v1.playback import router as playback_router
from app.api.v1.sessions import router as sessions_router
from prometheus_fastapi_instrumentator import Instrumentator
app = FastAPI(
    title="StreamOps Playback Service",
    version="1.0.0",
    description="Playback streaming microservice for StreamOps Reliability Platform"
)
Instrumentator().instrument(app).expose(app)
app.include_router(playback_router)
app.include_router(sessions_router)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "playback-service"
    }
