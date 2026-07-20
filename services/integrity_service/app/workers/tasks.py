from .celery_worker import celery_app

from ..database import SessionLocal
from ..incident_model import Incident



@celery_app.task
def create_incident_task(
    service,
    severity,
    message
):

    db = SessionLocal()


    try:

        incident = Incident(

            service=service,

            severity=severity,

            message=message,

            status="OPEN"

        )


        db.add(incident)

        db.commit()

        db.refresh(incident)


        return {

            "incident_id": incident.id,

            "status": "created"

        }


    finally:

        db.close()