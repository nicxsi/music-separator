import shutil
from asyncio import to_thread
from pathlib import Path
from typing import BinaryIO

from app.application.interfaces.repository_interface import IFileRepository


class FileRepository(IFileRepository):
    def __init__(self, upload_dir: Path, output_dir: Path):
        self.upload_dir = upload_dir
        self.output_dir = output_dir

    async def save_upload(self, file_stream: BinaryIO,
                          filename: str, job_id: str) -> Path:
        file_path = self.upload_dir / f"{job_id}_{filename}"

        await to_thread(self._save_file, file_stream, file_path)

        return file_path

    def get_zip_path(self, job_id: str) -> Path:
        return self.output_dir / f"{job_id}.zip"

    async def create_zip_archive(self, job_id: str, filename: str) -> Path:
            # Find out the folder name (Demucs takes file name
            # whithout extension)
            stem = Path(filename).stem
            source_dir = self.output_dir / "htdemucs" / f"{job_id}_{stem}"

            # Path to save zipzip (shutil in itself adds
            # extension .zip to the end)
            zip_target = self.output_dir / job_id

            if not source_dir.exists():
                raise FileNotFoundError(
                    "No separated tracks were found "
                    f"along the path: {source_dir}"
                )

            # Run sync shutil.make_archive in thread
            await to_thread(
                shutil.make_archive,
                base_name=str(zip_target),  # Archive name (without .zip)
                format="zip",               # Archive format
                root_dir=str(source_dir)    # Archived folder
            )

            return self.get_zip_path(job_id)

    @staticmethod
    def _save_file(file_stream: BinaryIO, path: Path):
        with open(path, "wb") as buffer:
            # Reads data in 1 MB chunks at a time
            # 1024 bytes is the optimal size to read
            while chunk := file_stream.read(1024 * 1024):
                buffer.write(chunk)
