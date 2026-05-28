from abc import ABC, abstractmethod

from app.domain.entities import Job


class IJobRepository(ABC):

    @abstractmethod
    async def create(self, job: Job) -> None:
        pass

    @abstractmethod
    async def update(self, job: Job) -> None:
        pass

    @abstractmethod
    async def get(self, job_id: str) -> Job | None:
        pass
