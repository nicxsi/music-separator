from abc import ABC, abstractmethod


class ITaskQueue(ABC):
    @abstractmethod
    def enqueue_separation(self, job_id: str, filename: str) -> None:
        pass
