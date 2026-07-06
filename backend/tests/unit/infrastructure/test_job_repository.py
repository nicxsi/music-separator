from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

import pytest

from app.domain.entities import Job, JobStatus
from app.infrastructure.database.models.job_model import JobORM
from app.infrastructure.repositories.job_repository import JobRepository


class FakeSession:
    def __init__(self):
        self.add = Mock()
        self.commit = AsyncMock()
        self.get = AsyncMock()


@pytest.mark.asyncio
async def test_create_adds_orm_object_and_commits():
    session = FakeSession()
    repo = JobRepository(session=session)

    job_id = str(uuid4())
    job = Job(id=job_id, filename="song.mp3", status=JobStatus.PENDING)

    await repo.create(job)

    assert session.add.call_count == 1
    assert session.commit.await_count == 1

    orm = session.add.call_args.args[0]
    # Extracting the ORM model that was created inside the repository
    # and passed to the session.add() method
    assert isinstance(orm, JobORM)
    assert orm.id == UUID(job_id)
    assert orm.filename == "song.mp3"
    assert orm.status == "pending"
    assert orm.error is None


@pytest.mark.asyncio
async def test_get_returns_domain_job_when_record_exists():
    session = FakeSession()
    repo = JobRepository(session=session)

    job_uuid = uuid4()
    session.get.return_value = JobORM(
        id=job_uuid,
        filename="song.mp3",
        status="processing",
        error=None,
    )

    result = await repo.get(str(job_uuid))

    assert result is not None
    assert result.id == str(job_uuid)
    assert result.filename == "song.mp3"
    assert result.status == JobStatus.PROCESSING
    assert result.error is None
    session.get.assert_awaited_once_with(JobORM, job_uuid)


@pytest.mark.asyncio
async def test_get_returns_none_when_record_missing():
    session = FakeSession()
    repo = JobRepository(session=session)

    session.get.return_value = None

    result = await repo.get(str(uuid4()))

    assert result is None


@pytest.mark.asyncio
async def test_update_mutates_orm_and_commits():
    session = FakeSession()
    repo = JobRepository(session=session)

    job_uuid = uuid4()
    existing = JobORM(
        id=job_uuid,
        filename="song.mp3",
        status="processing",
        error="old error",
    )
    session.get.return_value = existing

    job = Job(
        id=str(job_uuid),
        filename="song.mp3",
        status=JobStatus.COMPLETED,
        error=None,
    )

    await repo.update(job)

    assert existing.status == "completed"
    assert existing.error is None
    assert session.commit.await_count == 1
    session.get.assert_awaited_once_with(JobORM, job_uuid)


@pytest.mark.asyncio
async def test_update_does_not_commit_when_record_missing():
    session = FakeSession()
    repo = JobRepository(session=session)

    session.get.return_value = None

    job = Job(
        id=str(uuid4()),
        filename="song.mp3",
        status=JobStatus.FAILED,
        error="boom"
    )

    with pytest.raises(LookupError, match="Job not found for update"):
        await repo.update(job)

    assert session.commit.await_count == 0
