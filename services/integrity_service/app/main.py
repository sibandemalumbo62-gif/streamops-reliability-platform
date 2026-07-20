from fastapi import FastAPI

from .routes import router
from .incident_routes import router as incident_router

app = FastAPI(
    title="Integrity Service",
    version="0.1.0"
)


@app.get("/")
def health_check():
    return {
        "status": "running",
        "service": "integrity-service"
    }


print("BEFORE INCLUDE:", app.routes)


app.include_router(router)
app.include_router(incident_router)

print("AFTER INCLUDE:", app.routes)