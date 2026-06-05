from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO


class IFileRepository(ABC):
    """
    Saves the incoming byte stream of the audio file to disk
    :param file_stream: The binary data stream of the file
    :param filename: The original file name (for extracting the extension)
    :param job_id: The unique id of the task (used in the prefix of the name)
    :return: Path to the saved file
    """

    @abstractmethod
    def save_upload(self, file_stream: BinaryIO,
                          filename: str, job_id: str) -> Path:
        pass

    @abstractmethod
    def get_upload_path(self, job_id: str, filename: str) -> Path:
        pass

    @abstractmethod
    def get_zip_path(self, job_id: str) -> Path:
        pass

    @abstractmethod
    def create_zip_archive(self, job_id: str, filename: str) -> Path:
        pass
