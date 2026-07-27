from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from .database import get_db
from .job_model import Job
from .job_schemas import JobResponse
from .workers.tasks import run_integrity_job


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)



@router.post("/run", response_model=JobResponse)
def start_job(
    db: Session = Depends(get_db)
):

    job = Job(

        job_type="INTEGRITY_CHECK",

        status="PENDING",

        progress=0

    )


    db.add(job)

    db.commit()

    db.refresh(job)


    run_integrity_job.delay(job.id)


    return job
@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):

    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )


    if not job:

        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )


    return job