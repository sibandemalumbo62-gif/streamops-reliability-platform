from prometheus_client import Gauge

from .database import SessionLocal
from .alert_model import Alert
from .reliability_model import ReliabilityMetric
from .metrics import active_incidents_metric
from .incident_model import Incident
from .metrics import (
    active_incidents_metric,
    total_incidents_metric
)
reliability_score_metric = Gauge(
    "service_reliability_score",
    "Current reliability score of a service",
    ["service"]
)


error_budget_metric = Gauge(
    "service_error_budget_remaining",
    "Remaining error budget percentage",
    ["service"]
)


active_alert_metric = Gauge(
    "service_active_alerts",
    "Number of active alerts for a service",
    ["service"]
)


def update_reliability_metrics():

    db = SessionLocal()

    try:

        # Reliability score + error budget
        reliability_records = db.query(
            ReliabilityMetric
        ).all()


        for record in reliability_records:

            service = record.service


            # Reliability score
            reliability_score_metric.labels(
                service=service
            ).set(
                record.reliability_score
            )


            # Error budget calculation
            error_budget = record.reliability_score

            error_budget_metric.labels(
                service=service
            ).set(
                error_budget
            )


        # Active alerts
        alerts = db.query(Alert).filter(
            Alert.resolved == False
        ).all()


        alert_counts = {}


        for alert in alerts:

            alert_counts[alert.service] = (
                alert_counts.get(alert.service, 0) + 1
            )


        for service, count in alert_counts.items():

            active_alert_metric.labels(
                service=service
            ).set(500)


        # Active incidents
        incidents = db.query(Incident).filter(
            Incident.status == "OPEN"
        ).all()

        active_incidents_metric.set(
            len(incidents)
        )

    finally:
        db.close()
                # Incident metrics

        total_incidents = db.query(
            Incident
        ).count()


        active_incidents = db.query(
            Incident
        ).filter(
            Incident.status == "OPEN"
        ).count()


        total_incidents_metric.set(
            total_incidents
        )


        active_incidents_metric.set(
            active_incidents
        )