from pydantic import BaseModel
from datetime import datetime



class EventCreate(BaseModel):

    event_id: str

    event_type: str

    user_id: str

    service: str

    timestamp: datetime



class EventResponse(BaseModel):

    id: int

    event_id: str

    event_type: str

    user_id: str

    service: str

    timestamp: datetime


    class Config:

        from_attributes = True