from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .database import get_db
from .incident_model import Incident


router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"]
)



# =====================================
# GET ALL INCIDENTS
# =====================================

@router.get("/")
def get_incidents(
    db: Session = Depends(get_db)
):

    incidents = (
        db.query(Incident)
        .all()
    )


    return incidents




# =====================================
# GET SINGLE INCIDENT
# =====================================

@router.get("/{incident_id}")
def get_incident(

    incident_id: int,

    db: Session = Depends(get_db)

):

    incident = (

        db.query(Incident)

        .filter(
            Incident.id == incident_id
        )

        .first()

    )


    if not incident:

        raise HTTPException(

            status_code=404,

            detail="Incident not found"

        )


    return incident





# =====================================
# UPDATE INCIDENT STATUS
# =====================================

@router.patch("/{incident_id}")
def update_incident(

    incident_id: int,

    status: str,

    db: Session = Depends(get_db)

):


    incident = (

        db.query(Incident)

        .filter(
            Incident.id == incident_id
        )

        .first()

    )


    if not incident:

        raise HTTPException(

            status_code=404,

            detail="Incident not found"

        )



    allowed_status = [

        "OPEN",

        "INVESTIGATING",

        "RESOLVED"

    ]



    if status not in allowed_status:

        raise HTTPException(

            status_code=400,

            detail=(
                "Invalid status. "
                "Use OPEN, INVESTIGATING, or RESOLVED"
            )

        )



    incident.status = status


    db.commit()


    db.refresh(incident)



    return {

        "message": "Incident status updated",

        "incident": incident

    }