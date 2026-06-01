from app.core.config import settings
from celery import Celery

celery_app = Celery(
    "music_separator",
    broker=settings.RABBITMQ_URL
)
