from app.application.services.separation_service import SeparationService
from app.dependencies import get_separation_service
from app.presentation.schemas.pydantic_models import JobResponse, SeparationResponse
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

router = APIRouter()


@router.post("/separate", response_model=SeparationResponse, status_code=202)
async def separate(
    file: UploadFile = File(...),
    service: SeparationService = Depends(get_separation_service),
):
    """
    Creates an audio file separation task
    Gets an audio file (mp3, wav, flac), saves it to temporary storage,
    and sends a task to the Celery queue for processing by
    the Demucs neural network.
    Returns `job_id` to track the status.
    """
    filename = file.filename
    if filename is None:
        raise HTTPException(
            status_code=400, detail="Failed while reading a filename."
        )

    try:
        job = await service.submit(file_stream=file.file, filename=filename)
        return SeparationResponse(job_id=job.id, status=job.status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/download/{job_id}")
async def download(
    job_id: str,
    service: SeparationService = Depends(get_separation_service)
):
    """
    Creates a zip-archive with audio lines
    Sends the finished archive
    """
    try:
        zip_path = await service.get_result(job_id)
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
    service: SeparationService = Depends(get_separation_service)
):
    """
    Retrieves the status and details of a specific separation job
    """
    try:
        job = await service.get_job(job_id)
        return JobResponse(
            job_id=job.id,
            status=job.status,
            filename=job.filename,
            error=job.error
        )
    except LookupError:
        raise HTTPException(status_code=404, detail="Job not found")
