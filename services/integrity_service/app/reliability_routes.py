from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .database import get_db
from .reliability_model import ReliabilityMetric


router = APIRouter(
    prefix="/reliability",
    tags=["Reliability"]
)


@router.get("/")
def get_reliability(
    db: Session = Depends(get_db)
):

    metrics = (
        db.query(ReliabilityMetric)
        .all()
    )

    return metrics