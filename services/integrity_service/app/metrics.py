from prometheus_client import Counter
from prometheus_client import Gauge

from .database import SessionLocal
from .alert_model import Alert
from .incident_model import Incident
events_received = Counter(
    "events_received_total",
    "Total events received"
)


events_rejected = Counter(
    "events_rejected_total",
    "Total rejected events"
)
# Demo traffic values for dashboard testing
events_received.inc(1000)
events_rejected.inc(25)
incidents_created = Counter(
    "incidents_created_total",
    "Total incidents created"
)


active_incidents_metric = Gauge(
    "active_incidents",
    "Number of currently open incidents"
)
total_incidents_metric = Gauge(
    "total_incidents",
    "Total number of incidents created"
)
incident_severity_metric = Gauge(
    "incident_severity_count",
    "Number of incidents grouped by severity",
    ["severity"]
)




MTTR = Gauge(
    "service_mttr_minutes",
    "Mean time to recovery",
    ["service"]
)

# Default value so Prometheus always sees the metric
MTTR.labels(
    service="playback"
).set(0)

def update_active_alerts():
    db = SessionLocal()

    try:
        alerts = db.query(Alert).filter(
            Alert.resolved == False
        ).all()

        service_counts = {}

        for alert in alerts:
            service_counts[alert.service] = (
                service_counts.get(alert.service, 0) + 1
            )

        

    finally:
        db.close()


def update_mttr():

    db = SessionLocal()

    try:
        incidents = db.query(Incident).filter(
            Incident.resolved_at.isnot(None)
        ).all()

        service_times = {}

        for incident in incidents:

            recovery_time = (
                incident.resolved_at -
                incident.created_at
            ).total_seconds() / 60

            service_times.setdefault(
                incident.service,
                []
            ).append(recovery_time)


        for service, times in service_times.items():

            average_mttr = sum(times) / len(times)

            MTTR.labels(
                service=service
            ).set(average_mttr)


    finally:
        db.close()


def update_incident_severity():

    db = SessionLocal()

    try:

        incidents = db.query(Incident).all()

        severity_counts = {}

        for incident in incidents:

            severity_counts[incident.severity] = (
                severity_counts.get(incident.severity, 0) + 1
            )


        for severity, count in severity_counts.items():

            incident_severity_metric.labels(
                severity=severity
            ).set(count)


    finally:
        db.close()