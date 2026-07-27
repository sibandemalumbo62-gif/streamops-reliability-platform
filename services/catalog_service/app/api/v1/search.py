from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.content import ContentSearchResponse
from app.repositories.content_repository import search_content


router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


@router.get("/", response_model=ContentSearchResponse)
def search_content_endpoint(
    q: str = Query(..., min_length=1, description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    try:
        results = search_content(db, q, skip, limit)
        return {
            "count": len(results),
            "results": results
        }
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(error)}"
        )
