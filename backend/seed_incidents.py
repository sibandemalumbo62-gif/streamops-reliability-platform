import json
import urllib.request

services = [
    "api-gateway",
    "authentication",
    "payment-service",
    "order-service",
    "user-service",
    "notification-service",
    "recommendation-service",
    "search-service",
    "catalog-service",
    "inventory-service",
    "checkout-service",
    "stream-service",
    "playback-service",
    "analytics-service",
    "event-service",
    "profile-service",
    "subscription-service",
    "billing-service",
    "reporting-service",
    "media-service",
]

incidents = [
    ("High API latency", "API response latency exceeded 2 seconds", "high"),
    ("Elevated error rate", "HTTP 500 error rate increased above threshold", "high"),
    ("Service unavailable", "Service became temporarily unavailable", "critical"),
    ("Database latency", "Database queries are taking longer than expected", "medium"),
    ("Event processing delay", "Events are experiencing increased processing latency", "medium"),
    ("Consumer lag detected", "Consumer lag increased beyond the configured threshold", "high"),
    ("Authentication failures", "Authentication failure rate increased", "high"),
    ("Timeout errors", "Requests are timing out intermittently", "medium"),
    ("CPU utilization high", "CPU utilization exceeded the warning threshold", "medium"),
    ("Memory utilization high", "Memory utilization exceeded the warning threshold", "medium"),
    ("Dependency failure", "A downstream dependency is returning errors", "high"),
    ("Traffic spike", "Unexpected traffic increase detected", "medium"),
    ("SLO violation", "Service is currently outside its SLO target", "critical"),
    ("Error budget burn", "Error budget is being consumed faster than expected", "high"),
    ("Network latency", "Network latency increased significantly", "medium"),
    ("Failed event ingestion", "Event ingestion failures detected", "high"),
    ("Database connection issue", "Database connection failures detected", "critical"),
    ("Slow requests", "Request latency exceeded the configured threshold", "low"),
    ("Queue backlog", "Message queue backlog increased significantly", "high"),
    ("Health check failure", "Service health checks are failing", "critical"),
]

statuses = [
    "open",
    "open",
    "open",
    "investigating",
    "resolved",
]

created = 0

for i in range(50):
    service = services[i % len(services)]
    title, description, severity = incidents[i % len(incidents)]
    status = statuses[i % len(statuses)]

    payload = {
        "service": service,
        "title": f"{title} #{i + 1}",
        "description": description,
        "severity": severity,
        "status": status
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        "http://127.0.0.1:8000/api/incidents/",
        data=data,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(request) as response:
            result = json.loads(response.read().decode("utf-8"))
            created += 1
            print(
                f"Created {result.get('incident_number', 'INC')} | "
                f"{service} | {severity} | {status}"
            )

    except Exception as e:
        print(f"ERROR creating incident #{i + 1}: {e}")

print()
print(f"Finished. Created {created} incidents.")
