from .celery_worker import celery_app

from ..database import SessionLocal
from ..incident_model import Incident

from ..job_model import Job
import time
from sqlalchemy import func

from ..models import Event
from ..job_report_model import JobReport
@celery_app.task(
    name="run_integrity_job"
)
def run_integrity_job(job_id):

    db = SessionLocal()

    try:

        job = (
            db.query(Job)
            .filter(Job.id == job_id)
            .first()
        )


        job.status = "RUNNING"

        job.progress = 10

        db.commit()

        print(f"Running integrity analysis for job {job_id}")

        total_events = db.query(Event).count()

        accepted_events = (
            db.query(Event)
            .filter(Event.status == "ACCEPTED")
            .count()
        )

        rejected_events = (
            db.query(Event)
            .filter(Event.status == "REJECTED")
            .count()
        )

        if total_events > 0:

            success_rate = (
                accepted_events / total_events
            ) * 100

            failure_rate = (
                rejected_events / total_events
            ) * 100

        else:

            success_rate = 0

            failure_rate = 0


        report = JobReport(

            job_id=job.id,

            total_events=total_events,

            accepted_events=accepted_events,

            rejected_events=rejected_events,

            success_rate=round(success_rate, 2),

            failure_rate=round(failure_rate, 2)

        )

        db.add(report)

        db.commit()


        job.status = "COMPLETED"

        job.progress = 100


        db.commit()


        return {
            "job_id": job_id,
            "status": "completed"
        }


    finally:

        db.close()
@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=5,
    name="services.integrity_service.app.workers.tasks.create_incident_task"
)
def create_incident_task(
    self,
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

        # Update Prometheus metric
        

        print(
            f"Incident created successfully: {incident.id}"
        )


        return {

            "incident_id": incident.id,

            "status": "created"

        }


    except Exception as exc:

        db.rollback()

        print(
            f"Incident creation failed: {str(exc)}"
        )


        raise self.retry(
            exc=exc,
            countdown=5
        )


    finally:

        db.close()