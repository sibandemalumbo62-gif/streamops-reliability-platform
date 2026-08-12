import random
import uuid
from datetime import datetime, timedelta

from app.database import SessionLocal
from app.models.models import Event

# ============================================================
# CONFIGURATION
# ============================================================

SERVICES = [
    "playback",
    "recommendation",
    "catalog",
    "authentication",
    "payments",
    "streaming",
]

EVENT_TYPES = [
    "PLAYBACK_STARTED",
    "PLAYBACK_COMPLETED",
    "PLAYBACK_FAILED",
    "RECOMMENDATION_GENERATED",
    "CATALOG_UPDATED",
    "USER_AUTHENTICATED",
    "PAYMENT_PROCESSED",
    "STREAM_STARTED",
    "STREAM_COMPLETED",
    "STREAM_FAILED",
]

# Number of events to create
EVENTS_PER_SERVICE = 200

# Percentage chance of an event failing
FAILURE_RATE = 0.08


# ============================================================
# LATENCY GENERATION
# ============================================================

def generate_latency(service: str, failed: bool) -> int:

    if failed:
        # Failed events are generally slower
        return random.randint(300, 1500)

    # Different services have different normal latency
    latency_ranges = {
        "playback": (50, 250),
        "recommendation": (40, 180),
        "catalog": (80, 350),
        "authentication": (30, 200),
        "payments": (100, 500),
        "streaming": (60, 300),
    }

    minimum, maximum = latency_ranges.get(
        service,
        (50, 300),
    )

    return random.randint(
        minimum,
        maximum,
    )


# ============================================================
# EVENT GENERATOR
# ============================================================

def create_seed_events():

    db = SessionLocal()

    try:

        total_created = 0

        print()
        print("==========================================")
        print(" StreamOps Event Seeder")
        print("==========================================")
        print()

        for service in SERVICES:

            print(
                f"Generating {EVENTS_PER_SERVICE} events "
                f"for {service}..."
            )

            for _ in range(EVENTS_PER_SERVICE):

                event_type = random.choice(
                    EVENT_TYPES
                )

                failed = (
                    random.random()
                    < FAILURE_RATE
                )

                status = (
                    "failed"
                    if failed
                    else "processed"
                )

                latency = generate_latency(
                    service,
                    failed,
                )

                event = Event(
                    event_id=f"evt-{uuid.uuid4()}",
                    event_type=event_type,
                    service=service,
                    processing_latency_ms=latency,
                    status=status,
                )

                db.add(event)

                total_created += 1

            db.commit()

        print()
        print("==========================================")
        print(" Seeding complete")
        print("==========================================")
        print()
        print(
            f"Total events created: {total_created}"
        )

    except Exception as error:

        db.rollback()

        print()
        print("ERROR while creating events:")
        print(error)
        print()

        raise

    finally:

        db.close()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    create_seed_events()