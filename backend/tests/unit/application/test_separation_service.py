from io import BytesIO
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.application.interfaces.job_repository_interface import IJobRepository
from app.application.services.separation_service import SeparationService
from app.domain.entities import Job, JobStatus


def make_service():
    repo = Mock()
    job_repo = Mock(spec=IJobRepository)
    task_queue = Mock()
    service = SeparationService(
        repository=repo,
        job_repository=job_repo,
        task_queue=task_queue,
    )
    return service, repo, job_repo, task_queue


async def _run_in_thread(func, *args, **kwargs):
    return func(*args, **kwargs)


@pytest.mark.asyncio
@pytest.mark.parametrize("filename", ["song.mp3", "song.wav", "song.flac"])
async def test_submit_creates_job_saves_file_and_enqueues_task(filename):
    service, repo, job_repo, task_queue = make_service()

    repo.save_upload = Mock(return_value=Path("/fake/path"))
    job_repo.create = AsyncMock()

    file_stream = BytesIO(b"audio-bytes")

    # We replace asyncio.to_thread with direct work in the current thread so
    # that the test runs linearly without creating real OS background threads
    with patch(
        "app.application.services.separation_service.asyncio.to_thread",
        new=_run_in_thread,
    ):
        job = await service.submit(file_stream=file_stream, filename=filename)

    assert job.filename == filename
    assert job.status == JobStatus.PENDING

    job_repo.create.assert_awaited_once()
    created_job = job_repo.create.await_args.args[0]
    assert created_job.filename == filename
    assert created_job.status == JobStatus.PENDING

    repo.save_upload.assert_called_once_with(file_stream, filename, job.id)
    task_queue.enqueue_separation.assert_called_once_with(job.id, filename)


@pytest.mark.asyncio
async def test_submit_rejects_unsupported_format():
    service, repo, job_repo, task_queue = make_service()

    repo.save_upload = Mock()
    job_repo.create = AsyncMock()

    with pytest.raises(ValueError, match="Unsupported file format: txt"):
        await service.submit(file_stream=BytesIO(b"data"), filename="song.txt")

    job_repo.create.assert_not_called()
    repo.save_upload.assert_not_called()
    task_queue.enqueue_separation.assert_not_called()


@pytest.mark.asyncio
async def test_get_result_returns_zip_path_when_job_completed(tmp_path):
    service, repo, job_repo, task_queue = make_service()

    job = Job(id="job-1", filename="song.mp3", status=JobStatus.COMPLETED)
    job_repo.get = AsyncMock(return_value=job)

    zip_path = tmp_path / "job-1.zip"
    zip_path.write_text("test")
    repo.get_zip_path = Mock(return_value=zip_path)

    result = await service.get_result("job-1")

    assert result == zip_path
    job_repo.get.assert_awaited_once_with("job-1")
    repo.get_zip_path.assert_called_once_with("job-1")


@pytest.mark.asyncio
async def test_get_result_raises_lookup_error_when_job_missing():
    service, repo, job_repo, task_queue = make_service()

    job_repo.get = AsyncMock(return_value=None)

    with pytest.raises(LookupError, match="Job not found: job-404"):
        await service.get_result("job-404")


@pytest.mark.asyncio
async def test_get_result_raises_value_error_when_job_not_completed():
    service, repo, job_repo, task_queue = make_service()

    job = Job(id="job-1", filename="song.mp3", status=JobStatus.PROCESSING)
    job_repo.get = AsyncMock(return_value=job)

    with pytest.raises(ValueError, match="Job not completed: processing"):
        await service.get_result("job-1")


@pytest.mark.asyncio
async def test_get_result_raises_file_not_found_when_zip_missing(tmp_path):
    service, repo, job_repo, task_queue = make_service()

    job = Job(id="job-1", filename="song.mp3", status=JobStatus.COMPLETED)
    job_repo.get = AsyncMock(return_value=job)

    zip_path = tmp_path / "job-1.zip"  # not created
    repo.get_zip_path = Mock(return_value=zip_path)

    with pytest.raises(FileNotFoundError, match="Result file missing for job: job-1"):
        await service.get_result("job-1")


@pytest.mark.asyncio
async def test_get_job_returns_job_when_found():
    service, repo, job_repo, task_queue = make_service()

    job = Job(id="job-1", filename="song.mp3")
    job_repo.get = AsyncMock(return_value=job)

    result = await service.get_job("job-1")

    assert result is job
    job_repo.get.assert_awaited_once_with("job-1")


@pytest.mark.asyncio
async def test_get_job_raises_lookup_error_when_missing():
    service, repo, job_repo, task_queue = make_service()

    job_repo.get = AsyncMock(return_value=None)

    with pytest.raises(LookupError, match="Job not found: job-404"):
        await service.get_job("job-404")
