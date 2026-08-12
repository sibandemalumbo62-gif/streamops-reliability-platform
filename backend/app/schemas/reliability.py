from datetime import datetime

from pydantic import BaseModel


class ReliabilityResponse(BaseModel):

    id: int

    service: str

    availability: float

    success_rate: float

    error_rate: float

    latency_ms: float

    throughput: float

    consumer_lag_seconds: float

    reliability_score: float

    updated_at: datetime

    class Config:
        from_attributes = True