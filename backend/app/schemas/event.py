from pydantic import BaseModel


class EventCreate(BaseModel):
    event_id: str
    event_type: str
    service: str
    processing_latency_ms: float | None = None
    status: str = "processed"


class EventResponse(BaseModel):
    id: int
    event_id: str
    event_type: str
    service: str
    processing_latency_ms: float | None
    status: str

    class Config:
        from_attributes = True