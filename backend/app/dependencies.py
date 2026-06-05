from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.separation_service import SeparationService
from app.core.config import settings
from app.infrastructure.database.deps import get_db
from app.infrastructure.messaging.celery_task_queue import CeleryTaskQueue
from app.infrastructure.repositories.file_repository import FileRepository
from app.infrastructure.repositories.job_repository import JobRepository


def get_separation_service(
    session: AsyncSession = Depends(get_db)
) -> SeparationService:
    repo = FileRepository(
        upload_dir=settings.UPLOAD_DIR,
        output_dir=settings.OUTPUT_DIR
    )

    job_repo = JobRepository(session=session)

    task_queue = CeleryTaskQueue()

    return SeparationService(
        repository=repo,
        job_repository=job_repo,
        task_queue=task_queue
    )
