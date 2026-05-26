import uuid
from dataclasses import dataclass, field
from enum import Enum


class JobStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Job:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    filename: str = ""
    status: JobStatus = JobStatus.PENDING
    error: str | None = None

    def start_processing(self) -> None:
        self.status = JobStatus.PROCESSING

    def complete(self) -> None:
        self.status = JobStatus.COMPLETED
        self.error = None

    def fail(self, error: Exception | str) -> None:
        self.status = JobStatus.FAILED
        self.error = str(error)
