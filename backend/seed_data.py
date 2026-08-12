from app.database import SessionLocal, engine, Base
from app.models.models import (
    Service,
    ReliabilityMetric,
    SLO,
    Incident,
)

# Make sure tables exist
Base.metadata.create_all(bind=engine)

db = SessionLocal()

services = [
    {
        "name": "playback",
        "description": "Video playback and streaming service",
        "status": "healthy",
    },
    {
        "name": "recommendation",
        "description": "Content recommendation engine",
        "status": "healthy",
    },
    {
        "name": "authentication",
        "description": "User authentication and authorization",
        "status": "healthy",
    },
    {
        "name": "user-profile",
        "description": "User profile management service",
        "status": "healthy",
    },
    {
        "name": "catalog",
        "description": "Content catalog service",
        "status": "healthy",
    },
    {
        "name": "search",
        "description": "Content search service",
        "status": "healthy",
    },
    {
        "name": "payments",
        "description": "Payment processing service",
        "status": "degraded",
    },
    {
        "name": "notifications",
        "description": "Email and push notification service",
        "status": "healthy",
    },
    {
        "name": "analytics",
        "description": "Analytics and event processing service",
        "status": "healthy",
    },
    {
        "name": "content-delivery",
        "description": "Content delivery and CDN integration",
        "status": "healthy",
    },
    {
        "name": "subscription",
        "description": "Subscription and membership service",
        "status": "healthy",
    },
    {
        "name": "watchlist",
        "description": "User watchlist management service",
        "status": "healthy",
    },
    {
        "name": "streaming",
        "description": "Live streaming orchestration service",
        "status": "degraded",
    },
    {
        "name": "ads",
        "description": "Advertising and ad-insertion service",
        "status": "healthy",
    },
    {
        "name": "api-gateway",
        "description": "Central API gateway",
        "status": "healthy",
    },
]

for data in services:
    existing = (
        db.query(Service)
        .filter(Service.name == data["name"])
        .first()
    )

    if not existing:
        db.add(Service(**data))

db.commit()


# ---------------------------------------------------------
# RELIABILITY METRICS
# ---------------------------------------------------------

metrics = [
    ("playback", 99.97, 99.94, 0.06, 142, 8500, 0.8),
    ("recommendation", 99.91, 99.89, 0.11, 185, 6200, 1.2),
    ("authentication", 99.99, 99.98, 0.02, 95, 12800, 0.3),
    ("user-profile", 99.95, 99.92, 0.08, 120, 4300, 0.7),
    ("catalog", 99.98, 99.97, 0.03, 110, 7600, 0.4),
    ("search", 99.93, 99.90, 0.10, 155, 9100, 1.0),
    ("payments", 98.72, 98.41, 1.59, 420, 2100, 8.7),
    ("notifications", 99.87, 99.81, 0.19, 230, 5400, 1.9),
    ("analytics", 99.76, 99.68, 0.32, 310, 11800, 3.4),
    ("content-delivery", 99.99, 99.98, 0.02, 75, 25000, 0.2),
    ("subscription", 99.94, 99.91, 0.09, 130, 3200, 0.9),
    ("watchlist", 99.96, 99.94, 0.06, 105, 3800, 0.6),
    ("streaming", 99.21, 98.97, 1.03, 380, 4700, 6.2),
    ("ads", 99.89, 99.84, 0.16, 205, 6700, 1.5),
    ("api-gateway", 99.995, 99.99, 0.01, 65, 35000, 0.1),
]


for (
    service,
    availability,
    success_rate,
    error_rate,
    latency,
    throughput,
    lag,
) in metrics:

    existing = (
        db.query(ReliabilityMetric)
        .filter(ReliabilityMetric.service == service)
        .first()
    )

    if existing:
        existing.availability = availability
        existing.success_rate = success_rate
        existing.error_rate = error_rate
        existing.latency_ms = latency
        existing.throughput = throughput
        existing.consumer_lag_seconds = lag
    else:
        db.add(
            ReliabilityMetric(
                service=service,
                availability=availability,
                success_rate=success_rate,
                error_rate=error_rate,
                latency_ms=latency,
                throughput=throughput,
                consumer_lag_seconds=lag,
            )
        )

db.commit()


# ---------------------------------------------------------
# SLOs
# ---------------------------------------------------------

for service, availability, *_ in metrics:

    existing = (
        db.query(SLO)
        .filter(
            SLO.service == service,
            SLO.name == "Availability",
        )
        .first()
    )

    if not existing:

        target = 99.90

        if availability >= target:
            status = "meeting"
            budget = 100.0
        else:
            status = "breached"
            budget = max(0.0, (availability / target) * 100)

        db.add(
            SLO(
                service=service,
                name="Availability",
                target=target,
                current_value=availability,
                error_budget_remaining=budget,
                status=status,
            )
        )

db.commit()


# ---------------------------------------------------------
# INCIDENTS
# ---------------------------------------------------------

incidents = [
    {
        "incident_number": "INC-0001",
        "service": "payments",
        "title": "Elevated payment processing latency",
        "description": "Payment requests are experiencing increased latency.",
        "severity": "high",
        "status": "open",
    },
    {
        "incident_number": "INC-0002",
        "service": "streaming",
        "title": "Streaming degradation",
        "description": "Streaming service is experiencing increased error rates.",
        "severity": "high",
        "status": "open",
    },
    {
        "incident_number": "INC-0003",
        "service": "search",
        "title": "Search latency spike",
        "description": "Search response times exceeded the normal threshold.",
        "severity": "medium",
        "status": "resolved",
    },
    {
        "incident_number": "INC-0004",
        "service": "notifications",
        "title": "Notification delivery delays",
        "description": "Notification processing experienced temporary delays.",
        "severity": "low",
        "status": "resolved",
    },
]


for data in incidents:

    existing = (
        db.query(Incident)
        .filter(
            Incident.incident_number == data["incident_number"]
        )
        .first()
    )

    if not existing:
        db.add(Incident(**data))

db.commit()

print("==========================================")
print("StreamOps demo data successfully created")
print("==========================================")
print(f"Services: {db.query(Service).count()}")
print(f"Reliability metrics: {db.query(ReliabilityMetric).count()}")
print(f"SLOs: {db.query(SLO).count()}")
print(f"Incidents: {db.query(Incident).count()}")
print("==========================================")

db.close()
