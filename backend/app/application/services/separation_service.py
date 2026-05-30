from pathlib import Path
from typing import BinaryIO, ClassVar

from app.application.interfaces.audio_processor_interface import IAudioProcessor
from app.application.interfaces.job_repository_interface import IJobRepository
from app.application.interfaces.repository_interface import IFileRepository
from app.domain.entities import Job, JobStatus


class SeparationService:

    _ALLOWED_FORMATS: ClassVar[set[str]] = {"mp3", "wav", "flac"}


    def __init__(self, repository: IFileRepository,
                 audio_processor: IAudioProcessor,
                 job_repository: IJobRepository):
        self.repo = repository
        self.audio_processor = audio_processor
        self.job_repo = job_repository

    async def process(self, file_stream: BinaryIO, filename: str) -> Job:
        audio_format = Path(filename).suffix.removeprefix(".")

        if audio_format not in self._ALLOWED_FORMATS:
            raise ValueError(f"Unsupported file format: {audio_format}")

        job = Job(filename=filename)
        await self.job_repo.create(job)  # First, the job is pending

        job.start_processing()
        # Then, the job moves to a processing status
        await self.job_repo.update(job)

        try:
            input_path = await self.repo.save_upload(
                file_stream, filename, job.id
            )
            await self.audio_processor.run_separation(
                input_path, audio_format, job.id
            )
            # Create the zip archive with stems
            await self.repo.create_zip_archive(job.id, filename)

        except Exception as e:
            job.fail(e)
            await self.job_repo.update(job)
            raise

        job.complete()  # Finally, the job is completed
        await self.job_repo.update(job)
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
