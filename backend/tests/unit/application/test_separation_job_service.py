from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.application.interfaces.job_repository_interface import IJobRepository
from app.application.services.separation_job_service import SeparationJobService
from app.domain.entities import Job, JobStatus


async def _run_in_thread(func, *args, **kwargs):
    return func(*args, **kwargs)

def make_service():
    job_repo = Mock(spec=IJobRepository)
    file_repo = Mock()
    processor = Mock()
    service = SeparationJobService(
        job_repo=job_repo,
        file_repo=file_repo,
        processor=processor,
    )
    return service, job_repo, file_repo, processor


@pytest.mark.asyncio
async def test_process_missing_job_does_nothing():
    service, job_repo, file_repo, processor = make_service()

    job_repo.get = AsyncMock(return_value=None)
    job_repo.update = AsyncMock()

    await service.process("job-1", "song.mp3")

    job_repo.get.assert_awaited_once_with("job-1")
    job_repo.update.assert_not_called()
    file_repo.get_upload_path.assert_not_called()
    processor.run_separation.assert_not_called()
    file_repo.create_zip_archive.assert_not_called()


@pytest.mark.asyncio
async def test_process_success_updates_statuses_and_creates_zip():
    service, job_repo, file_repo, processor = make_service()

    # side_effect intercepts the state of the object at the time
    # of each update in the database, allowing us to check
    # the entire chain of status changes (PENDING -> PROCESSING -> COMPLETED)
    captured_statuses = []

    async def local_capture(job):
        captured_statuses.append(job.status)

    job = Job(id="job-1", filename="song.mp3")
    job_repo.get = AsyncMock(return_value=job)
    job_repo.update = AsyncMock(side_effect=local_capture)

    input_path = Path("/tmp/job-1_song.mp3")
    file_repo.get_upload_path = Mock(return_value=input_path)
    file_repo.create_zip_archive = Mock(return_value=Path("/tmp/job-1.zip"))
    processor.run_separation = Mock()

    # We replace asyncio.to_thread with direct work in the current thread so
    # that the test runs linearly without creating real OS background threads
    with patch(
        "app.application.services.separation_job_service.asyncio.to_thread",
        new=_run_in_thread,
    ):
        await service.process("job-1", "song.mp3")

    assert job.status == JobStatus.COMPLETED
    assert job.error is None
    assert captured_statuses == [
        JobStatus.PROCESSING,
        JobStatus.COMPLETED,
    ]
    assert job_repo.update.await_count == 2

    file_repo.get_upload_path.assert_called_once_with("job-1", "song.mp3")
    processor.run_separation.assert_called_once_with(
        input_path, "mp3", "job-1"
    )
    file_repo.create_zip_archive.assert_called_once_with("job-1", "song.mp3")


@pytest.mark.asyncio
async def test_process_failure_marks_job_failed_and_reraises():
    service, job_repo, file_repo, processor = make_service()

    # side_effect intercepts the state of the object at the time
    # of each update in the database, allowing us to check
    # the entire chain of status changes (PENDING -> PROCESSING -> COMPLETED)
    captured_statuses = []

    async def local_capture(job):
        captured_statuses.append(job.status)

    job = Job(id="job-1", filename="song.mp3")
    job_repo.get = AsyncMock(return_value=job)
    job_repo.update = AsyncMock(side_effect=local_capture)

    input_path = Path("/tmp/job-1_song.mp3")
    file_repo.get_upload_path = Mock(return_value=input_path)
    file_repo.create_zip_archive = Mock()

    processor.run_separation = Mock(side_effect=RuntimeError("boom"))

    # We replace asyncio.to_thread with direct work in the current thread so
    # that the test runs linearly without creating real OS background threads
    with patch(
        "app.application.services.separation_job_service.asyncio.to_thread",
        new=_run_in_thread,
    ):
        with pytest.raises(RuntimeError, match="boom"):
            await service.process("job-1", "song.mp3")

    assert job.status == JobStatus.FAILED
    assert job.error == "boom"

    assert captured_statuses == [
        JobStatus.PROCESSING,
        JobStatus.FAILED,
    ]

    assert job_repo.update.await_count == 2

    processor.run_separation.assert_called_once_with(
        input_path,
        "mp3",
        "job-1",
    )

    file_repo.create_zip_archive.assert_not_called()
