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

    @staticmethod
    def _save_file(file_stream: BinaryIO, path: Path):

        with open(path, "wb") as buffer:

            while chunk := file_stream.read(1024 * 1024):
                buffer.write(chunk)

    def get_zip_path(self, job_id: str) -> Path:
        return self.output_dir / f"{job_id}.zip"
