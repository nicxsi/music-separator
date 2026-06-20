from pathlib import Path

from app.application.services.separation_service import SeparationService
from app.dependencies import get_separation_service
from app.domain.entities import BrowserSession, JobStatus
from app.presentation.dependencies.browser_session import get_browser_session
from app.presentation.schemas.pydantic_models import JobResponse, SeparationResponse
from app.presentation.validators.file_size import validate_file_size
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

router = APIRouter()

_STEM_NAMES = ("vocals", "drums", "bass", "other")


def _build_stem_urls(job_id: str, filename: str) -> dict[str, str]:
    """
    Builds a dictionary {stem_name: url} for playback in the browser
    Demucs puts the results in:
      outputs/htdemucs/{job_id}_{filename_stem}/{vocals,drums,bass,other}.{ext}
    Where ext matches the input file format (mp3/flac/wav)
    """
    file_stem = Path(filename).stem          # "Example.flac" → "Example"
    audio_ext = Path(filename).suffix.lstrip(".")  # "flac"
    base = f"/outputs/htdemucs/{job_id}_{file_stem}"
    return {name: f"{base}/{name}.{audio_ext}" for name in _STEM_NAMES}


@router.post("/separate", response_model=SeparationResponse, status_code=202)
async def separate(
    file: UploadFile = File(...),
    browser_session: BrowserSession = Depends(get_browser_session),
    service: SeparationService = Depends(get_separation_service),
):
    """
    Creates an audio file separation task
    Gets an audio file (mp3, wav, flac), saves it to temporary storage,
    and sends a task to the Celery queue for processing by
    the Demucs neural network.
    Returns `job_id` to track the status.
    """
    await validate_file_size(file)

    filename = file.filename
    if filename is None:
        raise HTTPException(
            status_code=400, detail="Failed while reading a filename."
        )

    try:
        job = await service.submit(
            session_id=browser_session.id,
            file_stream=file.file,
            filename=filename,
        )
        return SeparationResponse(job_id=job.id, status=job.status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/download/{job_id}")
async def download(
    job_id: str,
    browser_session: BrowserSession = Depends(get_browser_session),
    service: SeparationService = Depends(get_separation_service),
):
    """
    Creates a zip-archive with audio lines
    Sends the finished archive
    """
    try:
        zip_path = await service.get_result(job_id, browser_session.id)
        return FileResponse(
            path=zip_path,
            media_type="application/zip",
            filename=f"{job_id}.zip"
        )
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/jobs/{job_id}")
async def get_job(
    job_id: str,
    browser_session: BrowserSession = Depends(get_browser_session),
    service: SeparationService = Depends(get_separation_service),
):
    """
    Retrieves the status and details of a specific separation job
    """
    try:
        job = await service.get_job(job_id, browser_session.id)

        stems = None
        if job.status == JobStatus.COMPLETED and job.filename:
            stems = _build_stem_urls(job_id, job.filename)

        return JobResponse(
            job_id=job.id,
            status=job.status,
            filename=job.filename,
            error=job.error,
            stems=stems,
        )
    except LookupError:
        raise HTTPException(status_code=404, detail="Job not found")
