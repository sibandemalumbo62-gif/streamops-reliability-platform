from prometheus_client import Counter, Gauge


events_received_total = Counter(
    "events_received_total",
    "Total number of events received by the StreamOps reliability platform",
)


incidents_created_total = Counter(
    "incidents_created_total",
    "Total number of reliability incidents created by StreamOps",
)


service_reliability_score = Gauge(
    "service_reliability_score",
    "Current reliability score for each monitored service",
    ["service"],
)


service_mttr_minutes = Gauge(
    "service_mttr_minutes",
    "Mean time to recovery in minutes for each monitored service",
    ["service"],
)