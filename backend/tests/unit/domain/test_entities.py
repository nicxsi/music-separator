from uuid import uuid4

from app.domain.entities import Job, JobStatus

session_id = uuid4()


def test_job_defaults():
    job = Job(session_id=session_id, filename="song.mp3")

    assert job.filename == "song.mp3"
    assert job.status == JobStatus.PENDING
    assert job.error is None
    assert isinstance(job.id, str)
    assert len(job.id) > 0


def test_job_start_processing_changes_status():
    job = Job(session_id=session_id, filename="song.mp3")

    job.start_processing()

    assert job.status == JobStatus.PROCESSING


def test_job_complete_sets_completed_and_clears_error():
    job = Job(session_id=session_id, filename="song.mp3", error="some error")

    job.complete()

    assert job.status == JobStatus.COMPLETED
    assert job.error is None


def test_job_fail_sets_failed_and_stores_error_string():
    job = Job(session_id=session_id, filename="song.mp3")

    job.fail(ValueError("boom"))

    assert job.status == JobStatus.FAILED
    assert job.error == "boom"
