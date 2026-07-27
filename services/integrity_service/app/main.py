
try:
    from fastapi import FastAPI  # type: ignore[import-not-found]
except ImportError:
    class FastAPI:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            pass

        def get(self, *args, **kwargs):
            def decorator(func):
                return func

            return decorator

        def on_event(self, *args, **kwargs):
            def decorator(func):
                return func

            return decorator

        def include_router(self, *args, **kwargs):
            return None

        def mount(self, *args, **kwargs):
            return None

try:
    from prometheus_client import make_asgi_app  # type: ignore[import-not-found]
except ImportError:
    def make_asgi_app():
        async def metrics_app(scope, receive, send):
            if scope["type"] != "http":
                return

            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [(b"content-type", b"text/plain; charset=utf-8")],
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": b"prometheus_client is not installed\n",
                }
            )

        return metrics_app

try:
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor  # type: ignore[import-not-found]
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor  # type: ignore[import-not-found]
except ImportError:
    class FastAPIInstrumentor:
        @staticmethod
        def instrument_app(app):
            return None

    class HTTPXClientInstrumentor:
        def instrument(self):
            return None

from . import tracing
from .routes import router
from .incident_routes import router as incident_router
from .alert_routes import router as alert_router
from .metrics_routes import router as metrics_router
from .job_routes import router as job_router
from .analytics_routes import router as analytics_router
from .job_report_routes import router as job_report_router
from prometheus_fastapi_instrumentator import Instrumentator
from .reliability_routes import router as reliability_router

from .metrics import (
    update_mttr,
    update_incident_severity
)
from .reliability_metrics import (
    update_reliability_metrics,
    reliability_score_metric,
    error_budget_metric,
    active_alert_metric,
)

app = FastAPI(
    title="StreamOps Integrity Service",
    version="1.0.0",
    description="Event validation and incident management microservice for StreamOps Reliability Platform"
)
Instrumentator().instrument(app).expose(app)
# OpenTelemetry
FastAPIInstrumentor.instrument_app(app)
HTTPXClientInstrumentor().instrument()


# Startup
@app.on_event("startup")
def startup_metrics():
    update_mttr()
    update_reliability_metrics()
    update_incident_severity()

# Health Check
@app.get("/")
def health_check():
    return {
        "status": "running",
        "service": "integrity-service"
    }


# Routers
app.include_router(router)
app.include_router(incident_router)
app.include_router(job_router)
app.include_router(job_report_router)
app.include_router(reliability_router)
app.include_router(alert_router)
app.include_router(analytics_router)
app.include_router(metrics_router)


# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics/", metrics_app)