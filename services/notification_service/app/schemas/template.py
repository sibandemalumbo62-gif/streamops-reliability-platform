from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel


class TemplateCreate(BaseModel):
    name: str
    notification_type: str
    channel: str
    subject_template: str
    body_template: str
    variables: Optional[str] = None


class TemplateUpdate(BaseModel):
    subject_template: Optional[str] = None
    body_template: Optional[str] = None
    variables: Optional[str] = None
    is_active: Optional[bool] = None


class TemplateResponse(BaseModel):
    id: UUID
    name: str
    notification_type: str
    channel: str
    subject_template: str
    body_template: str
    variables: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
