import asyncio
from pathlib import Path
from typing import BinaryIO, ClassVar

from app.application.interfaces.job_repository_interface import IJobRepository
from app.application.interfaces.repository_interface import IFileRepository
from app.application.interfaces.task_queue_interface import ITaskQueue
from app.application.utils import extract_audio_format
from app.domain.entities import Job, JobStatus


class SeparationService:

    _ALLOWED_FORMATS: ClassVar[set[str]] = {"mp3", "wav", "flac"}


    def __init__(self, repository: IFileRepository,
                 job_repository: IJobRepository, task_queue: ITaskQueue):
        self.repo = repository
        self.job_repo = job_repository
        self.task_queue = task_queue

    async def submit(self, file_stream: BinaryIO, filename: str) -> Job:
        audio_format = extract_audio_format(filename)

        if audio_format not in self._ALLOWED_FORMATS:
            raise ValueError(f"Unsupported file format: {audio_format}")

        job = Job(filename=filename)
        await self.job_repo.create(job)

        await asyncio.to_thread(self.repo.save_upload, file_stream, filename, job.id)
        self.task_queue.enqueue_separation(job.id, job.filename)

        return job

    async def get_result(self, job_id: str) -> Path:
        job = await self.job_repo.get(job_id)

        if job is None:
            raise LookupError(f"Job not found: {job_id}")

        if job.status != JobStatus.COMPLETED:
            raise ValueError(f"Job not completed: {job.status.value}")

        zip_path = self.repo.get_zip_path(job_id)

        if not zip_path.exists():
            raise FileNotFoundError(f"Result file missing for job: {job_id}")

        return zip_path

    async def get_job(self, job_id: str) -> Job:
        job = await self.job_repo.get(job_id)

        if job is None:
            raise LookupError(f"Job not found: {job_id}")

        return job
