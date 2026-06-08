from uuid import UUID

from app.domain.entities import Job, JobStatus
from app.infrastructure.database.models.job_model import JobORM


def to_domain(orm: JobORM) -> Job:
    return Job(
        id=str(orm.id),
        filename=orm.filename,
        status=JobStatus(orm.status),
        error=orm.error,
    )


def to_orm(domain: Job) -> JobORM:
    return JobORM(
        id=UUID(domain.id),
        filename=domain.filename,
        status=domain.status.value,
        error=domain.error,
    )
