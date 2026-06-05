"""
The Celery task module for background processing of heavy operations
All tasks here are performed inside the Celery worker in a synchronous context
"""

from pathlib import Path
from uuid import UUID

from app.core.config import settings
from app.domain.entities import JobStatus
from app.infrastructure.database.models.job_model import JobORM
from app.infrastructure.database.sync_engine import SyncSessionLocal
from app.infrastructure.messaging.celery_app import celery_app
from app.infrastructure.repositories.file_repository import FileRepository
from app.infrastructure.services.demucs_processor import DemucsProcessor
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


# Explicit task name protects against deserialization issues,
# if the folder structure on the API and the Workshop will differ minimally
@celery_app.task(name="app.infrastructure.tasks.tasks.process_job")
def process_job(job_id: str, filename: str) -> None:
    with SyncSessionLocal() as session:
        job_orm = session.get(JobORM, UUID(job_id))
        if job_orm is None:
            return

        try:
            # Step 1: We fix the start of processing
            job_orm.status = JobStatus.PROCESSING.value
            session.commit()

            # Step 2: Prepare the environment
            audio_format = Path(filename).suffix.removeprefix(".")
            repo = FileRepository(settings.UPLOAD_DIR, settings.OUTPUT_DIR)
            processor = DemucsProcessor(
                settings.OUTPUT_DIR, settings.DEMUCS_LOG_PATH
            )

            # Step 3: Heavy I/O and Computing operations
            input_path = repo.get_upload_path(job_id, filename)

            logger.info (f"Start track splitting for task {job_id}")
            processor.run_separation(input_path, audio_format, job_id)

            logger.info (f"Archiving results for task {job_id}")
            repo.create_zip_archive(job_id, filename)

            # Step 4: Record the successful completion
            job_orm.status = JobStatus.COMPLETED.value
            job_orm.error = None
            session.commit()

        except Exception as exc:
            session.rollback()
            job_orm.status = JobStatus.FAILED.value
            job_orm.error = str(exc)
            session.commit()

            logger.error(f"Error when processing task {job_id}: {str(exc)}",
                         exc_info=True
            )
            raise
