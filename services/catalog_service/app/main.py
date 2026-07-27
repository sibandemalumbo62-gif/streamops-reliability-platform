
from fastapi import FastAPI  # type: ignore[reportMissingImports]
from app.api.v1.catalog import router as catalog_router
from app.api.v1.search import router as search_router
from prometheus_fastapi_instrumentator import Instrumentator
app = FastAPI(
    title="StreamOps Catalog Service",
    version="1.0.0",
    description="Content catalog microservice for StreamOps Reliability Platform"
)
Instrumentator().instrument(app).expose(app)
app.include_router(catalog_router)
app.include_router(search_router)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "catalog-service"
    }
