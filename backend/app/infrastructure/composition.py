from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.separation_job_service import SeparationJobService
from app.core.config import settings
from app.infrastructure.repositories.file_repository import FileRepository
from app.infrastructure.repositories.job_repository import JobRepository
from app.infrastructure.services.demucs_processor import DemucsProcessor


def build_process_separation_service(
    session: AsyncSession
) -> SeparationJobService:
    """
    Wire the worker use case with concrete infrastructure implementations
    The API/worker code depends on abstractions in the application layer,
    while this function assembles the real repository, file storage,
    and Demucs processor for the Celery runtime
    """
    job_repo = JobRepository(session=session)
    file_repo = FileRepository(settings.UPLOAD_DIR, settings.OUTPUT_DIR)
    processor = DemucsProcessor(settings.OUTPUT_DIR, settings.DEMUCS_LOG_PATH)

    return SeparationJobService(
        job_repo=job_repo,
        file_repo=file_repo,
        processor=processor
    )
