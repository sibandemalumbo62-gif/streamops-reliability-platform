from sqlalchemy.orm import Session

from ..models.models import (
    Service,
    Event,
    Incident,
    ReliabilityMetric,
)

from ..metrics import (
    services_total,
    events_total,
    events_processed_total,
    events_failed_total,
    service_availability,
    service_success_rate,
    service_error_rate,
    service_latency_ms,
    service_throughput,
    service_consumer_lag,
    service_reliability_score,
    open_incidents,
    slo_compliance,
    error_budget_remaining,
    service_mttr_minutes,
)


def update_all_metrics(db: Session):

    # =========================================================
    # GLOBAL METRICS
    # =========================================================

    total_services = db.query(Service).count()

    total_events = db.query(Event).count()

    processed_events = (
        db.query(Event)
        .filter(Event.status == "processed")
        .count()
    )

    failed_events = (
        db.query(Event)
        .filter(Event.status != "processed")
        .count()
    )

    services_total.set(total_services)
    events_total.set(total_events)
    events_processed_total.set(processed_events)
    events_failed_total.set(failed_events)

    # =========================================================
    # OPEN INCIDENTS
    # =========================================================

    try:
        open_count = (
            db.query(Incident)
            .filter(Incident.status == "open")
            .count()
        )
    except Exception:
        open_count = 0

    open_incidents.set(open_count)

    # =========================================================
    # SERVICE METRICS
    # =========================================================

    services = db.query(Service).all()

    for service in services:

        service_name = service.name

        events = (
            db.query(Event)
            .filter(Event.service == service_name)
            .all()
        )

        if not events:
            service_availability.labels(
                service=service_name
            ).set(100)

            service_success_rate.labels(
                service=service_name
            ).set(100)

            service_error_rate.labels(
                service=service_name
            ).set(0)

            service_latency_ms.labels(
                service=service_name
            ).set(0)

            service_throughput.labels(
                service=service_name
            ).set(0)

            service_consumer_lag.labels(
                service=service_name
            ).set(0)

            service_reliability_score.labels(
                service=service_name
            ).set(100)

            slo_compliance.labels(
                service=service_name
            ).set(100)

            error_budget_remaining.labels(
                service=service_name
            ).set(100)

            service_mttr_minutes.labels(
                service=service_name
            ).set(0)

            continue

        total = len(events)

        successful = sum(
            1
            for event in events
            if event.status == "processed"
        )

        failed = total - successful

        success_rate = (
            successful / total
        ) * 100

        error_rate = (
            failed / total
        ) * 100

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

        # -----------------------------------------------------
        # Reliability score
        # -----------------------------------------------------

        reliability_score = (
            success_rate * 0.4
            + (100 - error_rate) * 0.3
            + max(
                0,
                100 - min(average_latency, 100)
            ) * 0.3
        )

        # -----------------------------------------------------
        # SLO
        # -----------------------------------------------------

        slo = min(
            100,
            success_rate
        )

        # Assume a 1% allowed error budget
        error_budget = max(
            0,
            100 - (error_rate / 1.0 * 100)
        )

        # -----------------------------------------------------
        # Update Prometheus
        # -----------------------------------------------------

        service_availability.labels(
            service=service_name
        ).set(round(success_rate, 2))

        service_success_rate.labels(
            service=service_name
        ).set(round(success_rate, 2))

        service_error_rate.labels(
            service=service_name
        ).set(round(error_rate, 2))

        service_latency_ms.labels(
            service=service_name
        ).set(round(average_latency, 2))

        service_throughput.labels(
            service=service_name
        ).set(total)

        service_consumer_lag.labels(
            service=service_name
        ).set(0)

        service_reliability_score.labels(
            service=service_name
        ).set(round(reliability_score, 2))

        slo_compliance.labels(
            service=service_name
        ).set(round(slo, 2))

        error_budget_remaining.labels(
            service=service_name
        ).set(round(error_budget, 2))

        # -----------------------------------------------------
        # MTTR
        # -----------------------------------------------------

        try:

            incidents = (
                db.query(Incident)
                .filter(
                    Incident.service == service_name
                )
                .all()
            )

            recovery_times = []

            for incident in incidents:

                if (
                    incident.created_at
                    and incident.resolved_at
                ):

                    minutes = (
                        incident.resolved_at
                        - incident.created_at
                    ).total_seconds() / 60

                    recovery_times.append(minutes)

            mttr = (
                sum(recovery_times)
                / len(recovery_times)
                if recovery_times
                else 0
            )

        except Exception:

            mttr = 0

        service_mttr_minutes.labels(
            service=service_name
        ).set(round(mttr, 2))