from sqlalchemy.orm import Session

from ..models.models import Event, ReliabilityMetric

from metrics.streamops_metrics import (
    service_reliability_score,
)


def calculate_reliability(
    db: Session,
    service_name: str,
):
    events = (
        db.query(Event)
        .filter(Event.service == service_name)
        .all()
    )

    if not events:
        return None

    total_events = len(events)

    successful_events = sum(
        1
        for event in events
        if event.status == "processed"
    )

    failed_events = total_events - successful_events

    success_rate = (
        successful_events / total_events
    ) * 100

    error_rate = (
        failed_events / total_events
    ) * 100

    latencies = [
        event.processing_latency_ms
        for event in events
        if event.processing_latency_ms is not None
    ]

    average_latency = (
        sum(latencies) / len(latencies)
        if latencies
        else 0.0
    )

    throughput = float(total_events)

    availability = success_rate

    reliability_score = (
        availability * 0.4
        + success_rate * 0.3
        + (100 - error_rate) * 0.2
        + max(
            0,
            100 - min(average_latency, 100),
        ) * 0.1
    )

    metric = (
        db.query(ReliabilityMetric)
        .filter(
            ReliabilityMetric.service == service_name
        )
        .first()
    )

    if metric is None:
        metric = ReliabilityMetric(
            service=service_name
        )

        db.add(metric)

    metric.availability = round(
        availability,
        2,
    )

    metric.success_rate = round(
        success_rate,
        2,
    )

    metric.error_rate = round(
        error_rate,
        2,
    )

    metric.latency_ms = round(
        average_latency,
        2,
    )

    metric.throughput = round(
        throughput,
        2,
    )

    metric.consumer_lag_seconds = 0.0

    metric.reliability_score = round(
        reliability_score,
        2,
    )

    db.commit()
    db.refresh(metric)

    # Prometheus
    service_reliability_score.labels(
        service=service_name
    ).set(
        reliability_score
    )

    return metric
