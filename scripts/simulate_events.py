import requests
import random
import time
from datetime import datetime


URL = "http://127.0.0.1:8009/events/"


services = [
    "playback",
    "auth",
    "catalog",
    "recommendation",
    "notification",
    "billing"
]


valid_events = [
    "LOGIN",
    "LOGOUT",
    "PLAYBACK_STARTED",
    "PLAYBACK_PAUSED",
    "PLAYBACK_RESUMED",
    "PLAYBACK_STOPPED"
]


invalid_events = [
    "BAD_EVENT",
    "UNKNOWN_EVENT",
    "INVALID_PLAYBACK",
    "FORGOTTEN_EVENT"
]


def send_event(i):

    service = random.choice(services)


    # 90% valid traffic
    if random.random() < 0.9:

        event_type = random.choice(valid_events)

    else:

        event_type = random.choice(invalid_events)


    payload = {

        "event_id": f"simulation_event_{i}",

        "event_type": event_type,

        "user_id": f"user_{random.randint(1,500)}",

        "service": service,

        "timestamp": datetime.utcnow().isoformat()

    }


    response = requests.post(
        URL,
        json=payload
    )


    print(
        i,
        service,
        event_type,
        response.status_code
    )



print("Starting StreamOps traffic simulation...")


for i in range(1,501):

    send_event(i)

    time.sleep(0.2)


print("Simulation completed")