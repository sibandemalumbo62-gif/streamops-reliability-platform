from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List

from app.models.content import Content


def get_content_by_id(db: Session, content_id: str):
    return (
        db.query(Content)
        .filter(Content.id == UUID(content_id))
        .first()
    )


def get_all_content(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    content_type: Optional[str] = None,
    is_available: Optional[bool] = None
):
    query = db.query(Content)
    
    if content_type:
        query = query.filter(Content.content_type == content_type)
    
    if is_available is not None:
        query = query.filter(Content.is_available == is_available)
    
    return (
        query
        .order_by(Content.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def search_content(
    db: Session,
    query: str,
    skip: int = 0,
    limit: int = 100
):
    search_pattern = f"%{query}%"
    return (
        db.query(Content)
        .filter(
            (Content.title.ilike(search_pattern)) |
            (Content.description.ilike(search_pattern)) |
            (Content.director.ilike(search_pattern))
        )
        .filter(Content.is_available == True)
        .order_by(Content.rating.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_content(db: Session, content_data: dict):
    new_content = Content(**content_data)
    db.add(new_content)
    db.commit()
    db.refresh(new_content)
    return new_content


def update_content(db: Session, content_id: str, content_data: dict):
    content = get_content_by_id(db, content_id)
    if not content:
        return None
    
    for key, value in content_data.items():
        setattr(content, key, value)
    
    db.commit()
    db.refresh(content)
    return content


def delete_content(db: Session, content_id: str):
    content = get_content_by_id(db, content_id)
    if not content:
        return False
    
    db.delete(content)
    db.commit()
    return True
