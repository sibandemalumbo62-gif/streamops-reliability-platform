from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.dependencies import get_db
from app.schemas.template import (
    TemplateCreate,
    TemplateUpdate,
    TemplateResponse
)
from app.repositories.template_repository import (
    create_template,
    get_template_by_id,
    get_template_by_name,
    get_all_templates,
    update_template,
    delete_template
)


router = APIRouter(
    prefix="/templates",
    tags=["Templates"],
)


@router.post("/", response_model=TemplateResponse, status_code=201)
def create_template_endpoint(
    template: TemplateCreate,
    db: Session = Depends(get_db)
):
    try:
        # Check if template name already exists
        existing = get_template_by_name(db, template.name)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Template with this name already exists"
            )
        
        new_template = create_template(db, template.model_dump())
        return new_template
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create template: {str(error)}"
        )


@router.get("/", response_model=List[TemplateResponse])
def get_all_templates_endpoint(
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    try:
        templates = get_all_templates(db, active_only)
        return templates
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch templates: {str(error)}"
        )


@router.get("/{template_id}", response_model=TemplateResponse)
def get_template_endpoint(
    template_id: str,
    db: Session = Depends(get_db)
):
    template = get_template_by_id(db, template_id)
    if not template:
        raise HTTPException(
            status_code=404,
            detail="Template not found"
        )
    return template


@router.patch("/{template_id}", response_model=TemplateResponse)
def update_template_endpoint(
    template_id: str,
    template_update: TemplateUpdate,
    db: Session = Depends(get_db)
):
    try:
        updated_template = update_template(
            db,
            template_id,
            template_update.model_dump(exclude_unset=True)
        )
        if not updated_template:
            raise HTTPException(
                status_code=404,
                detail="Template not found"
            )
        return updated_template
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update template: {str(error)}"
        )


@router.delete("/{template_id}")
def delete_template_endpoint(
    template_id: str,
    db: Session = Depends(get_db)
):
    try:
        success = delete_template(db, template_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Template not found"
            )
        return {"message": "Template deleted successfully"}
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete template: {str(error)}"
        )
