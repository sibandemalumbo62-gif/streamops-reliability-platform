from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .services.error_budget_analytics import get_error_budget
from .database import get_db
from .services.error_budget_analytics import get_error_budget
from .services.analytics_service import (
    calculate_mttr,
    calculate_incident_frequency,
    get_service_summary
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


@router.get("/mttr")
def get_mttr(
    db: Session = Depends(get_db)
):

    mttr = calculate_mttr(db)

    return {
        "metric": "MTTR",
        "value_minutes": mttr
    }
@router.get("/incidents")
def get_incident_frequency(
    db: Session = Depends(get_db)
):

    return calculate_incident_frequency(db)
@router.get("/service/{service_name}")
def service_summary(
    service_name: str,
    db: Session = Depends(get_db)
):

    return get_service_summary(
        db,
        service_name
    )
@router.get("/error-budget/{service_name}")
def error_budget(
    service_name: str,
    db: Session = Depends(get_db)
):

    return get_error_budget(
        db,
        service_name
    )