import asyncio
import logging

from app.application.interfaces.audio_processor_interface import IAudioProcessor
from app.application.interfaces.job_repository_interface import IJobRepository
from app.application.interfaces.repository_interface import IFileRepository
from app.application.utils import extract_audio_format

logger = logging.getLogger(__name__)


class SeparationJobService:
    """
    Worker-side use case for processing one separation job
    Loads the job from the database, moves it through the status lifecycle,
    runs Demucs, archives the result, and updates the final status
    """
    def __init__(
        self,
        job_repo: IJobRepository,
        file_repo: IFileRepository,
        processor: IAudioProcessor,
    ):
        self.job_repo = job_repo
        self.file_repo = file_repo
        self.processor = processor

    async def process(self, job_id: str, filename: str) -> None:
        job = await self.job_repo.get(job_id)
        # The job may be missing if the task was retried or
        # the DB record was deleted
        if job is None:
            logger.warning("Job %s not found in DB, skipping", job_id)
            return

        try:
            job.start_processing()
            await self.job_repo.update(job)

            input_path = self.file_repo.get_upload_path(job_id, filename)
            audio_format = extract_audio_format(filename)

            # Demucs CLI and zip creation are blocking operations
            # Run them in a thread so the async worker flow
            # does not block the event loop
            await asyncio.to_thread(
                self.processor.run_separation, input_path, audio_format, job_id
            )
            await asyncio.to_thread(
                self.file_repo.create_zip_archive, job_id, filename
            )

            job.complete()
            await self.job_repo.update(job)

        except Exception as exc:
            job.fail(exc)
            await self.job_repo.update(job)
            raise
