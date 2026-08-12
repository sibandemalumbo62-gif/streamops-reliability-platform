from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.models import Incident
from ..schemas.incident import IncidentCreate, IncidentResponse


router = APIRouter(
    prefix="/api/incidents",
    tags=["Incidents"],
)


@router.post("/", response_model=IncidentResponse)
def create_incident(
    incident: IncidentCreate,
    db: Session = Depends(get_db),
):
    count = db.query(Incident).count() + 1

    incident_number = f"INC-{count:04d}"

    new_incident = Incident(
        incident_number=incident_number,
        service=incident.service,
        title=incident.title,
        description=incident.description,
        severity=incident.severity,
        status="open",
    )

    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)

    return new_incident


@router.get("/", response_model=list[IncidentResponse])
def get_incidents(
    db: Session = Depends(get_db),
):
    return db.query(
        Incident
    ).order_by(
        Incident.id.desc()
    ).all()


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
):
    incident = db.query(Incident).filter(
        Incident.id == incident_id
    ).first()

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return incident


@router.patch("/{incident_id}/status", response_model=IncidentResponse)
def update_incident_status(
    incident_id: int,
    status: str,
    db: Session = Depends(get_db),
):
    incident = db.query(Incident).filter(
        Incident.id == incident_id
    ).first()

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    allowed_statuses = {
        "open",
        "investigating",
        "mitigated",
        "resolved",
    }

    if status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Use one of: {sorted(allowed_statuses)}",
        )

    incident.status = status

    if status == "resolved":
        incident.resolved_at = datetime.utcnow()

    db.commit()
    db.refresh(incident)

    return incident


@router.post("/{incident_id}/resolve", response_model=IncidentResponse)
def resolve_incident(
    incident_id: int,
    db: Session = Depends(get_db),
):
    incident = db.query(Incident).filter(
        Incident.id == incident_id
    ).first()

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    incident.status = "resolved"
    incident.resolved_at = datetime.utcnow()

    db.commit()
    db.refresh(incident)

    return incident
