from sqlalchemy.orm import Session
from uuid import UUID

from app.models.template import NotificationTemplate


def create_template(db: Session, template_data: dict):
    new_template = NotificationTemplate(**template_data)
    db.add(new_template)
    db.commit()
    db.refresh(new_template)
    return new_template


def get_template_by_id(db: Session, template_id: str):
    return (
        db.query(NotificationTemplate)
        .filter(NotificationTemplate.id == UUID(template_id))
        .first()
    )


def get_template_by_name(db: Session, name: str):
    return (
        db.query(NotificationTemplate)
        .filter(NotificationTemplate.name == name)
        .first()
    )


def get_all_templates(db: Session, active_only: bool = True):
    query = db.query(NotificationTemplate)
    
    if active_only:
        query = query.filter(NotificationTemplate.is_active == True)
    
    return query.all()


def update_template(db: Session, template_id: str, template_data: dict):
    template = get_template_by_id(db, template_id)
    if not template:
        return None
    
    for key, value in template_data.items():
        setattr(template, key, value)
    
    db.commit()
    db.refresh(template)
    return template


def delete_template(db: Session, template_id: str):
    template = get_template_by_id(db, template_id)
    if not template:
        return False
    
    db.delete(template)
    db.commit()
    return True
