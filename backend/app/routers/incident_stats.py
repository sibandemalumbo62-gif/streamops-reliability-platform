from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models.models import Incident


router = APIRouter(
    prefix="/api/incident-stats",
    tags=["Incident Statistics"],
)


@router.get("/")
def get_incident_statistics(
    db: Session = Depends(get_db),
):
    total = db.query(Incident).count()

    open_count = (
        db.query(Incident)
        .filter(Incident.status == "open")
        .count()
    )

    resolved_count = (
        db.query(Incident)
        .filter(Incident.status == "resolved")
        .count()
    )

    critical = (
        db.query(Incident)
        .filter(Incident.severity == "critical")
        .count()
    )

    high = (
        db.query(Incident)
        .filter(Incident.severity == "high")
        .count()
    )

    medium = (
        db.query(Incident)
        .filter(Incident.severity == "medium")
        .count()
    )

    low = (
        db.query(Incident)
        .filter(Incident.severity == "low")
        .count()
    )

    return {
        "total_incidents": total,
        "open_incidents": open_count,
        "resolved_incidents": resolved_count,
        "critical": critical,
        "high": high,
        "medium": medium,
        "low": low,
    }