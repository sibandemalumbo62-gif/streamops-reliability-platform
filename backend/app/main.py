from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from .routers import incident_stats
from .database import Base, engine, SessionLocal

from .services.metrics_service import update_all_metrics

from metrics.streamops_metrics import (
    events_received_total,
    incidents_created_total,
    service_reliability_score,
    service_mttr_minutes,
)

from .models.models import (
    Service,
    Event,
    ReliabilityMetric,
    SLO,
    Incident,
)

from .routers import (
    services,
    events,
    reliability,
    slos,
    incidents,
)


app = FastAPI(
    title="StreamOps Reliability Platform",
    version="1.0.0",
    description="REST API for monitoring event-stream reliability",
)


# ============================================================
# DATABASE
# ============================================================

Base.metadata.create_all(bind=engine)


# ============================================================
# INITIAL METRIC CALCULATION
# ============================================================

def refresh_metrics():
    db = SessionLocal()

    try:
        update_all_metrics(db)
    finally:
        db.close()


# Calculate metrics when backend starts
refresh_metrics()


# ============================================================
# API ROUTERS
# ============================================================

app.include_router(services.router)
app.include_router(events.router)
app.include_router(reliability.router)
app.include_router(slos.router)
app.include_router(incidents.router)
app.include_router(incident_stats.router)


# ============================================================
# PROMETHEUS
# ============================================================

Instrumentator().instrument(app).expose(
    app,
    endpoint="/metrics",
)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "name": "StreamOps Reliability Platform",
        "status": "running",
        "version": "1.0.0",
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
    }