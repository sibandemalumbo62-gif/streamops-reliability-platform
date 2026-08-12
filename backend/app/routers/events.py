from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.models import Event
from ..schemas.event import EventCreate, EventResponse

from ..services.reliability import calculate_reliability
from ..services.metrics_service import update_all_metrics
from ..services.incident_detector import detect_incident

from metrics.streamops_metrics import (
    events_received_total,
)


router = APIRouter(
    prefix="/api/events",
    tags=["Events"],
)


# ============================================================
# CREATE EVENT
# ============================================================

@router.post(
    "/",
    response_model=EventResponse,
)
def create_event(
    event: EventCreate,
    db: Session = Depends(get_db),
):

    # --------------------------------------------------------
    # Validate event status
    # --------------------------------------------------------

    allowed_statuses = {
        "processed",
        "failed",
    }

    status = event.status.lower()

    if status not in allowed_statuses:
        status = "processed"

    # --------------------------------------------------------
    # Create database event
    # --------------------------------------------------------

    new_event = Event(
        event_id=event.event_id,
        event_type=event.event_type,
        service=event.service,
        processing_latency_ms=event.processing_latency_ms,
        status=status,
    )

    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    # --------------------------------------------------------
    # Prometheus event counter
    # --------------------------------------------------------

    events_received_total.inc()

    # --------------------------------------------------------
    # Recalculate reliability
    # --------------------------------------------------------

    calculate_reliability(
        db,
        event.service,
    )

    # --------------------------------------------------------
    # Update all metrics
    # --------------------------------------------------------

    update_all_metrics(db)

    # --------------------------------------------------------
    # Automatic incident detection
    # --------------------------------------------------------

    detect_incident(
        db,
        event.service,
    )

    # --------------------------------------------------------
    # Update metrics again
    # This captures open_incidents after incident creation.
    # --------------------------------------------------------

    update_all_metrics(db)

    return new_event


# ============================================================
# GET EVENTS
# ============================================================

@router.get(
    "/",
    response_model=list[EventResponse],
)
def get_events(
    db: Session = Depends(get_db),
):

    return (
        db.query(Event)
        .order_by(Event.id.desc())
        .all()
    )