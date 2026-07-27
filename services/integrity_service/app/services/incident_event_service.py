from sqlalchemy.orm import Session

from ..incident_event_model import IncidentEvent


def create_incident_event(
    db: Session,
    alert_id: int,
    event_type: str
):

    event = IncidentEvent(
        alert_id=alert_id,
        event_type=event_type
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event