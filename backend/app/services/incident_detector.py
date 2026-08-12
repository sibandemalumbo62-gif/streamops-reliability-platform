from datetime import datetime
import uuid

from sqlalchemy.orm import Session

from ..models.models import Incident, Event


# ============================================================
# INCIDENT THRESHOLDS
# ============================================================

ERROR_RATE_THRESHOLD = 5.0
RELIABILITY_THRESHOLD = 80.0
LATENCY_THRESHOLD_MS = 500.0
SLO_THRESHOLD = 95.0


def generate_incident_number() -> str:
    """Generate a unique StreamOps incident number."""
    return f"INC-{uuid.uuid4().hex[:8].upper()}"


def detect_incident(
    db: Session,
    service_name: str,
):
    """
    Check service reliability and automatically create
    an incident when a reliability threshold is violated.
    """

    # ========================================================
    # GET SERVICE EVENTS
    # ========================================================

    events = (
        db.query(Event)
        .filter(Event.service == service_name)
        .all()
    )

    if not events:
        return None

    total_events = len(events)

    # ========================================================
    # CALCULATE SUCCESS / FAILURE
    # ========================================================

    failed_events = sum(
        1
        for event in events
        if event.status != "processed"
    )

    successful_events = total_events - failed_events

    success_rate = (
        successful_events / total_events
    ) * 100

    error_rate = (
        failed_events / total_events
    ) * 100

    # ========================================================
    # CALCULATE LATENCY
    # ========================================================

    latencies = [
        event.processing_latency_ms
        for event in events
        if event.processing_latency_ms is not None
    ]

    average_latency = (
        sum(latencies) / len(latencies)
        if latencies
        else 0
    )

    # ========================================================
    # CALCULATE RELIABILITY SCORE
    # ========================================================

    reliability_score = (
        success_rate * 0.4
        + (100 - error_rate) * 0.3
        + max(
            0,
            100 - min(average_latency, 100)
        ) * 0.3
    )

    # ========================================================
    # SLO
    # ========================================================

    slo_compliance = min(
        100,
        success_rate
    )

    # ========================================================
    # DETECT PROBLEM
    # ========================================================

    incident_title = None
    incident_description = None
    severity = "medium"

    # --------------------------------------------------------
    # ERROR RATE
    # --------------------------------------------------------

    if error_rate > ERROR_RATE_THRESHOLD:

        incident_title = "High Error Rate"

        incident_description = (
            f"Service '{service_name}' has an error rate "
            f"of {error_rate:.2f}%, exceeding the allowed "
            f"threshold of {ERROR_RATE_THRESHOLD}%."
        )

        severity = (
            "critical"
            if error_rate >= 10
            else "high"
        )

    # --------------------------------------------------------
    # RELIABILITY
    # --------------------------------------------------------

    elif reliability_score < RELIABILITY_THRESHOLD:

        incident_title = "Low Reliability Score"

        incident_description = (
            f"Service '{service_name}' has a reliability "
            f"score of {reliability_score:.2f}, below the "
            f"minimum threshold of {RELIABILITY_THRESHOLD}."
        )

        severity = (
            "critical"
            if reliability_score < 60
            else "high"
        )

    # --------------------------------------------------------
    # LATENCY
    # --------------------------------------------------------

    elif average_latency > LATENCY_THRESHOLD_MS:

        incident_title = "High Service Latency"

        incident_description = (
            f"Service '{service_name}' has an average "
            f"processing latency of "
            f"{average_latency:.2f} ms, exceeding the "
            f"threshold of {LATENCY_THRESHOLD_MS} ms."
        )

        severity = (
            "critical"
            if average_latency >= 1000
            else "high"
        )

    # --------------------------------------------------------
    # SLO
    # --------------------------------------------------------

    elif slo_compliance < SLO_THRESHOLD:

        incident_title = "SLO Violation"

        incident_description = (
            f"Service '{service_name}' has SLO compliance "
            f"of {slo_compliance:.2f}%, below the required "
            f"threshold of {SLO_THRESHOLD}%."
        )

        severity = (
            "critical"
            if slo_compliance < 90
            else "high"
        )

    # ========================================================
    # SERVICE IS HEALTHY
    # ========================================================

    if incident_title is None:
        return None

    # ========================================================
    # CHECK FOR EXISTING OPEN INCIDENT
    # ========================================================

    existing_incident = (
        db.query(Incident)
        .filter(
            Incident.service == service_name,
            Incident.status == "open",
        )
        .first()
    )

    if existing_incident:
        return existing_incident

    # ========================================================
    # CREATE INCIDENT
    # ========================================================

    incident = Incident(
        incident_number=generate_incident_number(),
        service=service_name,
        title=incident_title,
        description=incident_description,
        severity=severity,
        status="open",
        created_at=datetime.utcnow(),
    )

    db.add(incident)
    db.commit()
    db.refresh(incident)

    return incident