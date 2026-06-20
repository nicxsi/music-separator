from app.application.interfaces.session_repository_interface import (
    IBrowserSessionRepository,
)
from app.domain.entities import BrowserSession
from app.infrastructure.database.mappers.session_mapper import to_domain, to_orm
from app.infrastructure.database.models.browser_session_model import BrowserSessionORM
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class BrowserSessionRepository(IBrowserSessionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_token(self, token: str) -> BrowserSession | None:
        result = await self.session.execute(
            select(BrowserSessionORM).where(BrowserSessionORM.token == token)
        )
        orm = result.scalar_one_or_none()
        return to_domain(orm) if orm else None

    async def create(self, session: BrowserSession) -> None:
        orm = to_orm(session)
        self.session.add(orm)
        await self.session.commit()

    async def update(self, session: BrowserSession) -> None:
        orm = await self.session.get(BrowserSessionORM, session.id)
        if orm is None:
            raise LookupError(f"Session not found for update: {session.id}")

        orm.last_seen_at = session.last_seen_at
        orm.expires_at = session.expires_at
        await self.session.commit()
