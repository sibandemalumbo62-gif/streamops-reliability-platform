from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .services.incident_event_service import create_incident_event
from .database import SessionLocal
from .alert_model import Alert
from .alert_schemas import AlertResponse, AlertUpdate
from .incident_event_model import IncidentEvent
from .incident_event_schemas import IncidentEventResponse

router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[AlertResponse])
def get_alerts(
    db: Session = Depends(get_db)
):
    return db.query(Alert).all()
@router.patch("/{alert_id}")
def update_alert(
    alert_id: int,
    update: AlertUpdate,
    db: Session = Depends(get_db)
):

    alert = (
        db.query(Alert)
        .filter(Alert.id == alert_id)
        .first()
    )

    if not alert:
        return {
            "error": "Alert not found"
        }

    alert.status = update.status

    if update.status == "RESOLVED":
        alert.resolved = True

    create_incident_event(
        db=db,
        alert_id=alert.id,
        event_type="RESOLVED"
    )

    db.commit()
    db.refresh(alert)

    return alert
@router.get(
    "/{alert_id}/timeline",
    response_model=list[IncidentEventResponse]
)
def get_alert_timeline(
    alert_id: int,
    db: Session = Depends(get_db)
):

    events = (
        db.query(IncidentEvent)
        .filter(
            IncidentEvent.alert_id == alert_id
        )
        .order_by(
            IncidentEvent.created_at
        )
        .all()
    )

    return events