from fastapi import FastAPI

from services.auth_service.app.api.v1.auth import router as auth_router


app = FastAPI(

    title="StreamOps Auth Service",

    version="1.0.0",

    description="Authentication microservice for StreamOps Reliability Platform"

)


app.include_router(
    auth_router,
)


@app.get("/health")
def health_check():

    return {

        "status": "healthy",

        "service": "auth-service"

    }