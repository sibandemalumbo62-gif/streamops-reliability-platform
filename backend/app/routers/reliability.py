from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.models import ReliabilityMetric
from ..services.reliability_service import (
    calculate_reliability,
    calculate_all_reliability,
)
from ..schemas.reliability import ReliabilityResponse


router = APIRouter(
    prefix="/api/reliability",
    tags=["Reliability"],
)


@router.get(
    "/",
    response_model=list[ReliabilityResponse]
)
def get_reliability(
    db: Session = Depends(get_db),
):

    return (
        db.query(ReliabilityMetric)
        .order_by(
            ReliabilityMetric.reliability_score.desc()
        )
        .all()
    )


@router.post(
    "/calculate",
    response_model=list[ReliabilityResponse]
)
def calculate_reliability_metrics(
    db: Session = Depends(get_db),
):

    return calculate_all_reliability(db)


@router.post(
    "/calculate/{service_name}",
    response_model=ReliabilityResponse
)
def calculate_service_reliability(
    service_name: str,
    db: Session = Depends(get_db),
):

    metric = calculate_reliability(
        db,
        service_name
    )

    if metric is None:

        raise HTTPException(
            status_code=404,
            detail="No events found for this service"
        )

    return metric
