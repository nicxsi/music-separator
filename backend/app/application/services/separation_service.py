import asyncio
from pathlib import Path
from typing import BinaryIO, ClassVar
from uuid import UUID

from app.application.interfaces.job_repository_interface import IJobRepository
from app.application.interfaces.repository_interface import IFileRepository
from app.application.interfaces.task_queue_interface import ITaskQueue
from app.application.utils import extract_audio_format
from app.domain.entities import Job, JobStatus


class SeparationService:

    _ALLOWED_FORMATS: ClassVar[set[str]] = {"mp3", "wav", "flac"}


    def __init__(
        self,
        repository: IFileRepository,
        job_repository: IJobRepository,
        task_queue: ITaskQueue,
    ):
        self.repo = repository
        self.job_repo = job_repository
        self.task_queue = task_queue

    async def submit(
        self,
        session_id: UUID,
        file_stream: BinaryIO,
        filename: str,
    ) -> Job:
        audio_format = extract_audio_format(filename)

        if audio_format not in self._ALLOWED_FORMATS:
            raise ValueError(f"Unsupported file format: {audio_format}")

        job = Job(session_id=session_id, filename=filename)
        await self.job_repo.create(job)

        await asyncio.to_thread(
            self.repo.save_upload,
            file_stream,
            filename,
            str(job.id),
        )
        self.task_queue.enqueue_separation(str(job.id), job.filename)

        return job

    async def get_job(self, job_id: str, session_id: UUID) -> Job:
        return await self._get_owned_job(job_id, session_id)

    async def get_result(self, job_id: str, session_id: UUID) -> Path:
        job = await self._get_owned_job(job_id, session_id)

        if job.status != JobStatus.COMPLETED:
            raise ValueError(f"Job not completed: {job.status.value}")

        zip_path = self.repo.get_zip_path(job_id)

        if not zip_path.exists():
            raise FileNotFoundError(f"Result file missing for job: {job_id}")

        return zip_path

    async def _get_owned_job(self, job_id: str, session_id: UUID) -> Job:
        job = await self.job_repo.get(job_id)
        if job is None or job.session_id != session_id:
            raise LookupError(f"Job not found: {job_id}")
        return job
