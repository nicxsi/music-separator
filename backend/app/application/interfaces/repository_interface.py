from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO


class IFileRepository(ABC):

    @abstractmethod
    async def save_upload(self, file_stream: BinaryIO,
                          filename: str, job_id: str) -> Path:
        pass

    @abstractmethod
    def get_zip_path(self, job_id: str) -> Path:
        pass
