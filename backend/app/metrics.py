from prometheus_client import Gauge


services_total = Gauge(
    "streamops_services_total",
    "Total number of registered services",
)

events_total = Gauge(
    "streamops_events_total",
    "Total number of events",
)

events_processed_total = Gauge(
    "streamops_events_processed_total",
    "Total number of processed events",
)

events_failed_total = Gauge(
    "streamops_events_failed_total",
    "Total number of failed events",
)

service_availability = Gauge(
    "streamops_service_availability",
    "Service availability percentage",
    ["service"],
)

service_success_rate = Gauge(
    "streamops_service_success_rate",
    "Service success rate percentage",
    ["service"],
)

service_error_rate = Gauge(
    "streamops_service_error_rate",
    "Service error rate percentage",
    ["service"],
)

service_latency_ms = Gauge(
    "streamops_service_latency_ms",
    "Average service latency in milliseconds",
    ["service"],
)

service_throughput = Gauge(
    "streamops_service_throughput",
    "Service throughput",
    ["service"],
)

service_consumer_lag = Gauge(
    "streamops_service_consumer_lag_seconds",
    "Consumer lag in seconds",
    ["service"],
)

service_reliability_score = Gauge(
    "streamops_service_reliability_score",
    "Overall service reliability score",
    ["service"],
)

open_incidents = Gauge(
    "streamops_open_incidents",
    "Number of currently open incidents",
)

slo_compliance = Gauge(
    "streamops_slo_compliance",
    "SLO compliance percentage",
    ["service"],
)

error_budget_remaining = Gauge(
    "streamops_error_budget_remaining",
    "Remaining SLO error budget percentage",
    ["service"],
)

service_mttr_minutes = Gauge(
    "streamops_service_mttr_minutes",
    "Mean time to recovery in minutes",
    ["service"],
)