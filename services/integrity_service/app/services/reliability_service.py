from sqlalchemy.orm import Session

from ..models import Event
from ..reliability_model import ReliabilityMetric
from .alert_service import create_alert


def update_reliability(
    db: Session,
    service_name: str
):

    print(f"Updating reliability for {service_name}")

    total_events = (
        db.query(Event)
        .filter(Event.service == service_name)
        .count()
    )

    rejected_events = (
        db.query(Event)
        .filter(
            Event.service == service_name,
            Event.status == "REJECTED"
        )
        .count()
    )

    if total_events == 0:
        score = 100.0
    else:
        score = (
            (total_events - rejected_events)
            / total_events
        ) * 100

    print("Total events:", total_events)
    print("Rejected events:", rejected_events)
    print("Calculated score:", score)


    metric = (
        db.query(ReliabilityMetric)
        .filter(
            ReliabilityMetric.service == service_name
        )
        .first()
    )
    print("Existing metric:", metric)

    if metric is None:

        metric = ReliabilityMetric(
            service=service_name
        )

        db.add(metric)


    metric.total_events = total_events
    metric.rejected_events = rejected_events
    metric.reliability_score = round(score, 2)
    if metric.reliability_score < 90:
        create_alert(
            db=db,
            service=service_name,
            severity="WARNING",
            message=f"{service_name} reliability dropped below 90%"
        )

    db.commit()


   


    return metric