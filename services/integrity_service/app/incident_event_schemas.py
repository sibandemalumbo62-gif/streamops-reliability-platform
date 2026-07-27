from datetime import datetime
from pydantic import BaseModel


class IncidentEventResponse(BaseModel):

    id: int
    alert_id: int
    event_type: str
    created_at: datetime

    class Config:
        from_attributes = True