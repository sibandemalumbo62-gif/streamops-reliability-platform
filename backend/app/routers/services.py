from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.models import Service
from ..schemas.service import ServiceCreate, ServiceResponse


router = APIRouter(
    prefix="/api/services",
    tags=["Services"],
)


@router.post("/", response_model=ServiceResponse)
def create_service(
    service: ServiceCreate,
    db: Session = Depends(get_db),
):
    existing = (
        db.query(Service)
        .filter(Service.name == service.name)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Service already exists",
        )

    new_service = Service(
        name=service.name,
        description=service.description,
        status="healthy",
    )

    db.add(new_service)
    db.commit()
    db.refresh(new_service)

    return new_service


@router.get("/", response_model=list[ServiceResponse])
def get_services(
    db: Session = Depends(get_db),
):
    return (
        db.query(Service)
        .order_by(Service.id)
        .all()
    )
