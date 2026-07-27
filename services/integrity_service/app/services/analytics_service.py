from sqlalchemy.orm import Session
from datetime import datetime

from ..alert_model import Alert
from ..incident_event_model import IncidentEvent
from ..reliability_model import ReliabilityMetric


def calculate_mttr(db: Session):

    resolved_alerts = (
        db.query(Alert)
        .filter(Alert.resolved == True)
        .all()
    )

    if not resolved_alerts:
        return 0


    total_seconds = 0
    count = 0


    for alert in resolved_alerts:

        created_event = (
            db.query(IncidentEvent)
            .filter(
                IncidentEvent.alert_id == alert.id,
                IncidentEvent.event_type == "CREATED"
            )
            .first()
        )


        resolved_event = (
            db.query(IncidentEvent)
            .filter(
                IncidentEvent.alert_id == alert.id,
                IncidentEvent.event_type == "RESOLVED"
            )
            .first()
        )


        if created_event and resolved_event:

            duration = (
                resolved_event.created_at -
                created_event.created_at
            )

            total_seconds += duration.total_seconds()
            count += 1


    if count == 0:
        return 0


    return total_seconds / count / 60
def calculate_incident_frequency(db: Session):

    alerts = (
        db.query(Alert)
        .all()
    )

    total_incidents = len(alerts)

    services = {}

    for alert in alerts:

        if alert.service in services:
            services[alert.service] += 1
        else:
            services[alert.service] = 1

    return {
        "total_incidents": total_incidents,
        "services": services
    }
def get_service_summary(
    db: Session,
    service_name: str
):

    reliability = (
        db.query(ReliabilityMetric)
        .filter(
            ReliabilityMetric.service_name == service_name
        )
        .first()
    )


    incidents = (
        db.query(Alert)
        .filter(
            Alert.service == service_name
        )
        .count()
    )


    mttr = calculate_mttr(db)


    if reliability:

        score = reliability.reliability_score

    else:

        score = 0


    if score >= 99:

        status = "HEALTHY"

    elif score >= 90:

        status = "WARNING"

    else:

        status = "CRITICAL"


    return {
        "service": service_name,
        "reliability_score": score,
        "incidents": incidents,
        "mttr_minutes": mttr,
        "status": status
    }