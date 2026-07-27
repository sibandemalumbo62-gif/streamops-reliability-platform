from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.db.dependencies import get_db
from app.schemas.content import (
    ContentCreate,
    ContentUpdate,
    ContentResponse,
    ContentSearchResponse
)
from app.repositories.content_repository import (
    get_content_by_id,
    get_all_content,
    create_content,
    update_content,
    delete_content
)


router = APIRouter(
    prefix="/catalog",
    tags=["Catalog"],
)


@router.post("/", response_model=ContentResponse, status_code=201)
def create_content_endpoint(
    content: ContentCreate,
    db: Session = Depends(get_db)
):
    try:
        new_content = create_content(db, content.model_dump())
        return new_content
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create content: {str(error)}"
        )


@router.get("/", response_model=ContentSearchResponse)
def get_all_content_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    content_type: Optional[str] = Query(None),
    is_available: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    try:
        content_list = get_all_content(db, skip, limit, content_type, is_available)
        return {
            "count": len(content_list),
            "results": content_list
        }
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch content: {str(error)}"
        )


@router.get("/{content_id}", response_model=ContentResponse)
def get_content_endpoint(
    content_id: str,
    db: Session = Depends(get_db)
):
    content = get_content_by_id(db, content_id)
    if not content:
        raise HTTPException(
            status_code=404,
            detail="Content not found"
        )
    return content


@router.patch("/{content_id}", response_model=ContentResponse)
def update_content_endpoint(
    content_id: str,
    content_update: ContentUpdate,
    db: Session = Depends(get_db)
):
    try:
        updated_content = update_content(
            db,
            content_id,
            content_update.model_dump(exclude_unset=True)
        )
        if not updated_content:
            raise HTTPException(
                status_code=404,
                detail="Content not found"
            )
        return updated_content
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update content: {str(error)}"
        )


@router.delete("/{content_id}")
def delete_content_endpoint(
    content_id: str,
    db: Session = Depends(get_db)
):
    try:
        success = delete_content(db, content_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Content not found"
            )
        return {"message": "Content deleted successfully"}
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete content: {str(error)}"
        )
