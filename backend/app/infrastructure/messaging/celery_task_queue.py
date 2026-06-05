"""
Implementing a task queue interface using Celery
It belongs to the infrastructure adapter layer
"""

from app.application.interfaces.task_queue_interface import ITaskQueue


class CeleryTaskQueue(ITaskQueue):
    def enqueue_separation(self, job_id: str, filename: str) -> None:
        # IMPORTANT: Lazy import (inside the method) is used to prevent
        # Cyclic dependency (Circular Import).
        #
        # Module `tasks.py ` indirectly depends on
        # the application/infrastructure layers
        # that initialize this `CeleryTaskQueue'. If you import
        # `process_job` at the module level, Python will loop
        # when building the API container.
        from app.infrastructure.tasks.tasks import process_job

        # Sending a task to RabbitMQ asynchronously
        process_job.delay(job_id, filename)
