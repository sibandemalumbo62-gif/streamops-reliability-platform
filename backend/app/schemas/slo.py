from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SLOCreate(BaseModel):
    service: str
    name: str
    target: float


class SLOResponse(BaseModel):
    id: int
    service: str
    name: str
    target: float
    current_value: float
    error_budget_remaining: float
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
