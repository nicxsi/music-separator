from app.application.services.separation_service import SeparationService
from app.core.config import settings
from app.infrastructure.repositories.file_repository import FileRepository
from app.infrastructure.services.demucs_processor import DemucsProcessor


def get_separation_service() -> SeparationService:
    processor = DemucsProcessor(
        log_path=settings.DEMUCS_LOG_PATH,
        output_dir=settings.OUTPUT_DIR
    )

    repo = FileRepository(
        upload_dir=settings.UPLOAD_DIR,
        output_dir=settings.OUTPUT_DIR
    )

    return SeparationService(
        repository=repo,
        audio_processor=processor
    )
