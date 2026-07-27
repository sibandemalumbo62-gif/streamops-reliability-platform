from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from .metrics import events_received, events_rejected
from .database import get_db
from .models import Event

from .schemas import EventCreate
from .logger import logger
from .metrics import events_received, events_rejected
from .incident_model import Incident
from .workers.tasks import create_incident_task
from .services.reliability_service import update_reliability
router = APIRouter(
    
    tags=["Events"]
)



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



# =====================================
# INTEGRITY ENGINE
# =====================================

class IntegrityEngine:


    def validate_event(self, event):

        errors = []


        if not event.event_id:
            errors.append(
                "event_id is required"
            )


        if not event.event_type:
            errors.append(
                "event_type is required"
            )


        if not event.user_id:
            errors.append(
                "user_id is required"
            )


        if not event.service:
            errors.append(
                "service is required"
            )



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



# =====================================
# CREATE EVENT
# =====================================


@router.post("/events")
def create_event(

    event: EventCreate,

    db: Session = Depends(get_db)

):


    logger.info(
        f"Received event {event.event_id}"
    )
    events_received.inc()


    # Check duplicate event

    existing_event = (

        db.query(Event)

        .filter(
            Event.event_id == event.event_id
        )

        .first()

    )



    if existing_event:

        return {

            "status":"duplicate",

            "message":"Event already exists",

            "event_id":event.event_id

        }



    # Validate event

    validation = (

        integrity_engine

        .validate_event(event)

    )



    if validation["valid"]:

        event_status = "ACCEPTED"

        validation_error = None



    else:

        event_status = "REJECTED"

        events_rejected.inc()

        validation_error = ", ".join(
            validation["errors"]
        )



    # Create event record

    new_event = Event(

        event_id=event.event_id,

        event_type=event.event_type,

        user_id=event.user_id,

        service=event.service,

        timestamp=event.timestamp,

        status=event_status,

        validation_error=validation_error

    )



    db.add(new_event)

    db.commit()

    db.refresh(new_event)
    update_reliability(
    db,
    new_event.service
)

    incident_created = False

    if new_event.status == "REJECTED":
        try:
            create_incident_task.delay(
                service=new_event.service,
                severity="HIGH",
                message=new_event.validation_error
            )
        except Exception as e:
            # Log error but don't fail the request
            print(f"Failed to queue incident task: {e}")



    # =====================================
    # PHASE 4.1
    # CREATE INCIDENT AUTOMATICALLY
    # =====================================


    if new_event.status == "REJECTED":


        
            

        incident_created = True



        logger.warning(

            f"Incident created for rejected event {event.event_id}"

        )



    return {
        "status": "success",
        "message": "Event created successfully",
        "incident_created": incident_created,
        "event": {
            "id": new_event.id,
            "event_id": new_event.event_id,
            "event_type": new_event.event_type,
            "user_id": new_event.user_id,
            "service": new_event.service,
            "timestamp": new_event.timestamp,
            "status": new_event.status,
            "validation_error": new_event.validation_error
        }

    }





# =====================================
# GET ALL EVENTS
# =====================================


@router.get("/events")
def get_events(

    db: Session = Depends(get_db)

):

    return (

        db.query(Event)

        .all()

    )





# =====================================
# METRICS
# =====================================


@router.get("/stats")
def get_metrics(

    db:Session = Depends(get_db)

):


    total_events = (

        db.query(Event)

        .count()

    )


    accepted_events = (

        db.query(Event)

        .filter(
            Event.status=="ACCEPTED"
        )

        .count()

    )


    rejected_events = (

        db.query(Event)

        .filter(
            Event.status=="REJECTED"
        )

        .count()

    )



    success_rate = 0

    failure_rate = 0



    if total_events > 0:


        success_rate = (

            accepted_events / total_events

        ) * 100



        failure_rate = (

            rejected_events / total_events

        ) * 100



    return {


        "total_events":total_events,


        "accepted_events":accepted_events,


        "rejected_events":rejected_events,


        "success_rate":round(success_rate,2),


        "failure_rate":round(failure_rate,2)

    }





# =====================================
# HEALTH CHECK
# =====================================


@router.get("/health")
def get_health(
    db: Session = Depends(get_db)
):

    try:
        # Check database connection
        db.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "service": "integrity-service",
            "database": "connected"
        }

    except Exception as e:

        return {
            "status": "unhealthy",
            "service": "integrity-service",
            "database": "disconnected",
            "error": str(e)
        }
# =====================================
# FILTER EVENTS
# =====================================


@router.get("/filter")
def filter_events(

    status:str=None,

    service:str=None,

    event_type:str=None,

    db:Session=Depends(get_db)

):


    query = db.query(Event)



    if status:

        query=query.filter(
            Event.status==status
        )



    if service:

        query=query.filter(
            Event.service==service
        )



    if event_type:

        query=query.filter(
            Event.event_type==event_type
        )



    events=query.all()



    return {


        "count":len(events),


        "events":events

    }





# =====================================
# GET SINGLE EVENT
# =====================================


@router.get("/events/{event_id}")
def get_event(

    event_id:str,

    db:Session=Depends(get_db)

):


    event=(

        db.query(Event)

        .filter(
            Event.event_id==event_id
        )

        .first()

    )



    if not event:


        raise HTTPException(

            status_code=404,

            detail="Event not found"

        )



    return event