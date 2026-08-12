from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models.models import Service, Event, ReliabilityMetric, Incident, SLO

router = APIRouter(
    prefix="/api/statistics",
    tags=["Statistics"],
)


@router.get("/")
def get_statistics(
    db: Session = Depends(get_db),
):
    total_services = db.query(Service).count()
    total_events = db.query(Event).count()
    total_incidents = db.query(Incident).count()
    total_slos = db.query(SLO).count()

    healthy_services = db.query(Service).filter(
        Service.status == "healthy"
    ).count()

    degraded_services = db.query(Service).filter(
        Service.status == "degraded"
    ).count()

    critical_services = db.query(Service).filter(
        Service.status == "critical"
    ).count()

    total_errors = db.query(Event).filter(
        Event.status == "error"
    ).count()

    average_availability = db.query(
        func.avg(ReliabilityMetric.availability)
    ).scalar()

    average_success_rate = db.query(
        func.avg(ReliabilityMetric.success_rate)
    ).scalar()

    average_latency = db.query(
        func.avg(ReliabilityMetric.latency_ms)
    ).scalar()

    return {
        "total_services": total_services,
        "total_events": total_events,
        "total_incidents": total_incidents,
        "total_slos": total_slos,
        "healthy_services": healthy_services,
        "degraded_services": degraded_services,
        "critical_services": critical_services,
        "total_errors": total_errors,
        "average_availability": round(
            float(average_availability or 0), 2
        ),
        "average_success_rate": round(
            float(average_success_rate or 0), 2
        ),
        "average_latency_ms": round(
            float(average_latency or 0), 2
        ),
    }
