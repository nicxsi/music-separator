import asyncio
import socket

from app.infrastructure.composition import build_process_separation_service
from app.infrastructure.database.worker_session import WorkerSessionLocal
from app.infrastructure.messaging.celery_app import celery_app
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


async def run_process_job(job_id: str, filename: str) -> None:
    async with WorkerSessionLocal() as session:
        service = build_process_separation_service(session)
        await service.process(job_id, filename)


@celery_app.task(
    bind=True,
    name="app.infrastructure.tasks.tasks.process_job",
    autoretry_for=(socket.gaierror, OSError),
    max_retries=3,
    retry_backoff=True  # Exponential delay
)
def process_job(self, job_id: str, filename: str) -> None:
    """
    Simple task implementation: uses WorkerSessionLocal,
    builds the service, and runs the use case
    """
    logger.info("Task received: job_id=%s, file=%s", job_id, filename)
    try:
        asyncio.run(run_process_job(job_id, filename))
        logger.info("Task completed: job_id=%s", job_id)
    except (socket.gaierror, OSError) as exc:
        logger.warning(
            "Transient error occurred. Retrying task %s (%d/%d). Error: %s",
            self.request.retries,
            self.max_retries,
            exc,
        )
        raise
