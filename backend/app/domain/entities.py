from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from uuid import UUID, uuid4


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class JobStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Job:
    session_id: UUID
    id: str = field(default_factory=lambda: str(uuid4()))
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

@dataclass
class BrowserSession:
    token: str
    expires_at: datetime
    created_at: datetime = field(default_factory=_utcnow)
    last_seen_at: datetime = field(default_factory=_utcnow)
    id: UUID = field(default_factory=uuid4)

    def is_expired(self, now: datetime | None = None) -> bool:
        now = now or _utcnow()
        return now > self.expires_at

    def refresh(self, lifetime_days: int) -> None:
        now = _utcnow()
        self.last_seen_at = now
        self.expires_at = now + timedelta(days=lifetime_days)
