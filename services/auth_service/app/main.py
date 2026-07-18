from fastapi import FastAPI

app = FastAPI(
    title="StreamOps Auth Service",
    version="1.0.0",
    description="Authentication service for the StreamOps Reliability Platform."
)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "auth-service"
    }