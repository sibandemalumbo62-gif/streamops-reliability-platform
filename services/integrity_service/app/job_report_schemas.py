from pydantic import BaseModel
from datetime import datetime


class JobReportResponse(BaseModel):

    id: int

    job_id: int

    total_events: int

    accepted_events: int

    rejected_events: int

    success_rate: float

    failure_rate: float

    created_at: datetime

    class Config:
        from_attributes = True