from pydantic import BaseModel


class JobResponse(BaseModel):

    id: int

    job_type: str

    status: str

    progress: int

    requested_by: str | None

    class Config:
        from_attributes = True