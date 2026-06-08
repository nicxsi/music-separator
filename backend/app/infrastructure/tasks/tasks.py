import asyncio

from app.infrastructure.composition import build_process_separation_service
from app.infrastructure.database.worker_session import WorkerSessionLocal
from app.infrastructure.messaging.celery_app import celery_app
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


async def run_process_job(job_id: str, filename: str) -> None:
    async with WorkerSessionLocal() as session:
        service = build_process_separation_service(session)
        await service.process(job_id, filename)


@celery_app.task(name="app.infrastructure.tasks.tasks.process_job")
def process_job(job_id: str, filename: str) -> None:
    """
    Simple task implementation: uses WorkerSessionLocal,
    builds the service, and runs the use case
    """
    logger.info("Task received: job_id=%s, file=%s", job_id, filename)
    try:
        asyncio.run(run_process_job(job_id, filename))
        logger.info("Task completed: job_id=%s", job_id)
    except Exception:
        logger.exception("Task failed: job_id=%s", job_id)
        raise
