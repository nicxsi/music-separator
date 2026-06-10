from uuid import uuid4

import pytest
from app.domain.entities import Job, JobStatus
from app.infrastructure.database.mappers.job_mapper import to_domain, to_orm
from app.infrastructure.database.models.job_model import JobORM


def test_to_domain_maps_orm_to_domain():
    orm = JobORM(
        id=uuid4(),
        filename="song.mp3",
        status="completed",
        error=None,
    )

    job = to_domain(orm)

    assert job.id == str(orm.id)
    assert job.filename == "song.mp3"
    assert job.status == JobStatus.COMPLETED
    assert job.error is None


def test_to_orm_maps_domain_to_orm():
    job = Job(
        id=str(uuid4()),
        filename="song.mp3",
        status=JobStatus.FAILED,
        error="boom",
    )

    orm = to_orm(job)

    assert str(orm.id) == job.id
    assert orm.filename == "song.mp3"
    assert orm.status == "failed"
    assert orm.error == "boom"


def test_to_orm_raises_for_invalid_uuid():
    job = Job(
        id="not-a-uuid",
        filename="song.mp3",
        status=JobStatus.PENDING,
        error=None,
    )

    with pytest.raises(ValueError):
        to_orm(job)
