# pyright: reportMissingImports=false
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router

from app.db.init_db import init_db


# Create database tables
init_db()


app = FastAPI(

    title="StreamOps Auth Service",

    version="1.0.0",

    description="Authentication microservice for StreamOps Reliability Platform"
    
)
Instrumentator().instrument(app).expose(app)

app.include_router(auth_router)
app.include_router(users_router)


@app.get("/health")

def health_check():

    return {

        "status": "healthy",

        "service": "auth-service"

    }