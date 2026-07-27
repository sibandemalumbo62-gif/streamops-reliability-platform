from datetime import datetime
from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: int
    service: str
    severity: str
    message: str
    status: str
    resolved: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AlertUpdate(BaseModel):
    status: str