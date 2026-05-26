from app.domain.entities import JobStatus
from pydantic import BaseModel


class SeparationResponse(BaseModel):
    """
    After receiving files from the separate API, the response
    model is constructed.
    FastAPI is used for response validation and
    Swagger documentation generation.
    """
    job_id: str
    status: JobStatus

    model_config = {"from_attributes": True}
