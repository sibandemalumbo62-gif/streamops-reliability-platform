from sqlalchemy.orm import Session

from ..models import Event

VALID_EVENT_TYPES = [
    "PLAYBACK_STARTED",
    "PLAYBACK_PAUSED",
    "PLAYBACK_RESUMED",
    "PLAYBACK_STOPPED",
    "LOGIN",
    "LOGOUT"
]
VALID_SERVICES = [
    "playback",
    "auth",
    "catalog",
    "recommendation",
    "notification",
    "billing"
]

class IntegrityEngine:

    def validate_event(self, event):

        errors = []

        if not event.event_id:
            errors.append("event_id is required")

        if not event.event_type:
            errors.append("event_type is required")

        if not event.user_id:
            errors.append("user_id is required")

        if not event.service:
            errors.append("service is required")

        if event.event_type not in VALID_EVENT_TYPES:
            errors.append(
                f"Invalid event_type: {event.event_type}"
            )

        if event.service not in VALID_SERVICES:
            errors.append(
                f"Invalid service: {event.service}"
            )

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }


integrity_engine = IntegrityEngine()