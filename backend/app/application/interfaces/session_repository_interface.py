from abc import ABC, abstractmethod

from app.domain.entities import BrowserSession


class IBrowserSessionRepository(ABC):
    @abstractmethod
    async def get_by_token(self, token: str) -> BrowserSession | None:
        pass

    @abstractmethod
    async def create(self, session: BrowserSession) -> None:
        pass

    @abstractmethod
    async def update(self, session: BrowserSession) -> None:
        pass
