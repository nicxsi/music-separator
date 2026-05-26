from app.dependencies import get_separation_service
from app.presentation.schemas.pydantic_models import SeparationResponse
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

router = APIRouter()


@router.post("/separate", response_model=SeparationResponse)
async def separate(
    file: UploadFile = File(...),
    service = Depends(get_separation_service)
):
    filename = file.filename

    if filename is None:
        raise HTTPException(status_code=400, 
                            detail="Failed while reading a filename."
        )

    try:
        job = await service.process(file_stream=file.file, filename=filename)

        return SeparationResponse(job_id=job.id, status=job.status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# TODO: implement the GET request
'''
@router.get("/download/{job_id}")
async def download(
    job_id: str,
    service: SeparationService = Depends(get_separation_service)
):
    zip_path = await service.get_result(job_id)
    return FileResponse(zip_path, media_type="application/zip")
'''
