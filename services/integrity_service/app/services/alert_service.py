from sqlalchemy.orm import Session

from ..alert_model import Alert
from .incident_event_service import create_incident_event
def update_active_alerts():
    """
    Placeholder for updating active alerts state.
    Implementations should update any in-memory or external
    tracking of active alerts. Left as a no-op to avoid
    NameError when called.
    """
    return
def create_alert(
    db: Session,
    service: str,
    severity: str,
    message: str
):
    """
    Creates an alert only if an unresolved alert
    with the same service and severity doesn't exist.
    """

    existing_alert = (
        db.query(Alert)
        .filter(
            Alert.service == service,
            Alert.severity == severity,
            Alert.resolved == False
        )
        .first()
    )

    if existing_alert:
        return existing_alert

    alert = Alert(
        service=service,
        severity=severity,
        message=message
    )
    db.add(alert)
    db.commit()
    update_active_alerts()
    db.refresh(alert)

    create_incident_event(
        db=db,
        alert_id=alert.id,
        event_type="CREATED"
    )

    return alert