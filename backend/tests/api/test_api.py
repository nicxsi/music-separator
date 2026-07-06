import zipfile
from importlib import import_module
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.domain.entities import Job, JobStatus


class FakeSeparationService:
    def __init__(self):
        self.submit = AsyncMock()
        self.get_result = AsyncMock()
        self.get_job = AsyncMock()


@pytest.fixture
def app_instance(tmp_path):
    static_dir = tmp_path / "static"
    static_dir.mkdir()
    return import_module("app.main").create_app(static_dir=static_dir)

@pytest_asyncio.fixture
async def client(app_instance):
    async with AsyncClient(
        transport=ASGITransport(app=app_instance),
        base_url="http://test",
    ) as async_client:
        yield async_client
    # The code after yield will be executed automatically
    # AFTER the end of the test
    app_instance.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_separate_returns_202_and_job_payload(app_instance, client):
    deps = import_module("app.dependencies")
    fake_service = FakeSeparationService()
    fake_service.submit.return_value = Job(
        id="job-1",
        filename="song.mp3",
        status=JobStatus.PENDING,
    )

    app_instance.dependency_overrides[
        deps.get_separation_service
    ] = lambda: fake_service

    response = await client.post(
        "/api/separate",
        files={"file": ("song.mp3", b"audio-bytes", "audio/mpeg")},
    )

    assert response.status_code == 202
    assert response.json() == {
        "job_id": "job-1",
        "status": "pending",
    }
    fake_service.submit.assert_awaited_once()


@pytest.mark.asyncio
async def test_separate_returns_400_for_unsupported_format(
    app_instance,
    client
):
    deps = import_module("app.dependencies")
    fake_service = FakeSeparationService()
    fake_service.submit.side_effect = ValueError(
        "Unsupported file format: txt"
    )

    app_instance.dependency_overrides[
        deps.get_separation_service
    ] = lambda: fake_service

    response = await client.post(
        "/api/separate",
        files={"file": ("song.txt", b"plain-text", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported file format: txt"


@pytest.mark.asyncio
async def test_download_returns_zip_file(app_instance, client, tmp_path):
    deps = import_module("app.dependencies")
    fake_service = FakeSeparationService()

    zip_path = tmp_path / "job-1.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("vocals.txt", "voice")

    fake_service.get_result.return_value = zip_path
    app_instance.dependency_overrides[
        deps.get_separation_service
    ] = lambda: fake_service

    response = await client.get("/api/download/job-1")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/zip")
    assert response.content == zip_path.read_bytes()


@pytest.mark.asyncio
async def test_get_job_returns_job_payload(app_instance, client):
    deps = import_module("app.dependencies")
    fake_service = FakeSeparationService()
    fake_service.get_job.return_value = Job(
        id="job-1",
        filename="song.mp3",
        status=JobStatus.COMPLETED,
        error=None,
    )

    app_instance.dependency_overrides[
        deps.get_separation_service
    ] = lambda: fake_service

    response = await client.get("/api/jobs/job-1")

    assert response.status_code == 200
    assert response.json() == {
        "job_id": "job-1",
        "status": "completed",
        "filename": "song.mp3",
        "error": None,
    }


@pytest.mark.asyncio
async def test_get_job_returns_404_when_missing(app_instance, client):
    deps = import_module("app.dependencies")
    fake_service = FakeSeparationService()
    fake_service.get_job.side_effect = LookupError("Job not found: job-404")

    app_instance.dependency_overrides[
        deps.get_separation_service
    ] = lambda: fake_service

    response = await client.get("/api/jobs/job-404")

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"
