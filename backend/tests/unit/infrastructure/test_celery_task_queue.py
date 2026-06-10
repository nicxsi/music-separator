from unittest.mock import patch

from app.infrastructure.messaging.celery_task_queue import CeleryTaskQueue


@patch("app.infrastructure.tasks.tasks.process_job")
def test_enqueue_separation_calls_delay_on_celery_task(mock_process_job):
    queue = CeleryTaskQueue()
    queue.enqueue_separation("job-1", "song.mp3")
    mock_process_job.delay.assert_called_once_with("job-1", "song.mp3")
