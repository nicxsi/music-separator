"""
Celery Application Initialization and Configuration Module
Uses RabbitMQ as a message broker
'rpc://' is used as the backend for storing results,
which means transferring task states back through
the broker's temporary queues without permanent storage.
"""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "music_separator",
    broker=settings.RABBITMQ_URL,
    backend="rpc://",
    include=["app.infrastructure.tasks.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone=settings.TIMEZONE,
    enable_utc=True,
    task_track_started=True,
)
