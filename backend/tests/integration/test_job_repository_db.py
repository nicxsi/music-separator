from uuid import UUID

import pytest
from app.domain.entities import Job
from app.infrastructure.database.models.job_model import JobORM
from app.infrastructure.repositories.job_repository import JobRepository


@pytest.mark.asyncio
async def test_create_persists_job_in_postgres(db_session):
    repo = JobRepository(session=db_session)

    job = Job(filename="song.mp3")
    await repo.create(job)

    orm = await db_session.get(JobORM, UUID(job.id))

    assert orm is not None
    assert orm.filename == "song.mp3"
    assert orm.status == "pending"

@pytest.mark.asyncio
async def test_get_reads_job_from_database(db_session):
    repo = JobRepository(db_session)

    job = Job(filename="song.mp3")

    await repo.create(job)

    result = await repo.get(job.id)

    assert result is not None
    assert result.id == job.id
    assert result.filename == "song.mp3"

@pytest.mark.asyncio
async def test_update_updates_existing_record(db_session):
    repo = JobRepository(db_session)

    job = Job(filename="song.mp3")

    await repo.create(job)

    job.complete()

    await repo.update(job)

    orm = await db_session.get(
        JobORM,
        UUID(job.id),
    )

    assert orm.status == "completed"
