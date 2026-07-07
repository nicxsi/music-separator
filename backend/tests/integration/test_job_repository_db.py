from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest

from app.domain.entities import Job
from app.infrastructure.database.models.browser_session_model import BrowserSessionORM
from app.infrastructure.database.models.job_model import JobORM
from app.infrastructure.repositories.job_repository import JobRepository


@pytest.mark.asyncio
async def test_create_persists_job_in_postgres(db_session):
    now = datetime.now(UTC)

    session = BrowserSessionORM(
        id=uuid4(),
        token="test-token",
        created_at=now,
        last_seen_at=now,
        expires_at=now + timedelta(days=30),
    )

    db_session.add(session)
    await db_session.commit()

    repo = JobRepository(session=db_session)

    job = Job(session_id=session.id, filename="song.mp3")
    await repo.create(job)

    orm = await db_session.get(JobORM, UUID(job.id))

    assert orm is not None
    assert orm.filename == "song.mp3"
    assert orm.status == "pending"

@pytest.mark.asyncio
async def test_get_reads_job_from_database(db_session):
    now = datetime.now(UTC)

    session = BrowserSessionORM(
        id=uuid4(),
        token="test-token",
        created_at=now,
        last_seen_at=now,
        expires_at=now + timedelta(days=30),
    )

    db_session.add(session)
    await db_session.commit()

    repo = JobRepository(db_session)

    job = Job(session_id=session.id, filename="song.mp3")

    await repo.create(job)

    result = await repo.get(job.id)

    assert result is not None
    assert result.id == job.id
    assert result.filename == "song.mp3"

@pytest.mark.asyncio
async def test_update_updates_existing_record(db_session):
    now = datetime.now(UTC)

    session = BrowserSessionORM(
        id=uuid4(),
        token="test-token",
        created_at=now,
        last_seen_at=now,
        expires_at=now + timedelta(days=30),
    )

    db_session.add(session)
    await db_session.commit()

    repo = JobRepository(db_session)

    job = Job(session_id=session.id, filename="song.mp3")

    await repo.create(job)

    job.complete()

    await repo.update(job)

    orm = await db_session.get(
        JobORM,
        UUID(job.id),
    )

    assert orm.status == "completed"
