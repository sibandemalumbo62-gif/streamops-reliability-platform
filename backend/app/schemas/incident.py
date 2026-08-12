from pydantic import BaseModel


class IncidentCreate(BaseModel):
    service: str
    title: str
    description: str | None = None
    severity: str = "medium"


class IncidentResponse(BaseModel):
    id: int
    incident_number: str
    service: str
    title: str
    description: str | None
    severity: str
    status: str

    class Config:
        from_attributes = True
