from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.separation_service import SeparationService
from app.core.config import settings
from app.infrastructure.database.deps import get_db
from app.infrastructure.repositories.file_repository import FileRepository
from app.infrastructure.repositories.job_repository import JobRepository
from app.infrastructure.services.demucs_processor import DemucsProcessor


def get_separation_service(
    session: AsyncSession = Depends(get_db)
) -> SeparationService:
    processor = DemucsProcessor(
        log_path=settings.DEMUCS_LOG_PATH,
        output_dir=settings.OUTPUT_DIR
    )

    repo = FileRepository(
        upload_dir=settings.UPLOAD_DIR,
        output_dir=settings.OUTPUT_DIR
    )

    job_repo = JobRepository(session=session)

    return SeparationService(
        repository=repo,
        audio_processor=processor,
        job_repository=job_repo
    )
