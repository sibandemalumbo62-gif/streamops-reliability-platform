from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.models import SLO, Service
from ..schemas.slo import SLOCreate, SLOResponse


router = APIRouter(
    prefix="/api/slos",
    tags=["SLOs"],
)


@router.post("/", response_model=SLOResponse)
def create_slo(
    slo: SLOCreate,
    db: Session = Depends(get_db),
):
    service = db.query(Service).filter(
        Service.name == slo.service
    ).first()

    if not service:
        raise HTTPException(
            status_code=404,
            detail=f"Service '{slo.service}' not found",
        )

    if slo.target <= 0 or slo.target > 100:
        raise HTTPException(
            status_code=400,
            detail="SLO target must be between 0 and 100",
        )

    existing = db.query(SLO).filter(
        SLO.service == slo.service,
        SLO.name == slo.name,
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="SLO already exists for this service",
        )

    new_slo = SLO(
        service=slo.service,
        name=slo.name,
        target=slo.target,
        current_value=100.0,
        error_budget_remaining=100.0 - slo.target,
        status="meeting",
    )

    db.add(new_slo)
    db.commit()
    db.refresh(new_slo)

    return new_slo


@router.get("/", response_model=list[SLOResponse])
def get_slos(
    db: Session = Depends(get_db),
):
    return db.query(SLO).order_by(SLO.id).all()


@router.get("/{slo_id}", response_model=SLOResponse)
def get_slo(
    slo_id: int,
    db: Session = Depends(get_db),
):
    slo = db.query(SLO).filter(
        SLO.id == slo_id
    ).first()

    if not slo:
        raise HTTPException(
            status_code=404,
            detail="SLO not found",
        )

    return slo
