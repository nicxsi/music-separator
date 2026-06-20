import secrets
from datetime import datetime, timedelta, timezone

from app.application.interfaces.session_repository_interface import (
    IBrowserSessionRepository,
)
from app.domain.entities import BrowserSession


class BrowserSessionService:
    def __init__(self, repo: IBrowserSessionRepository, session_lifetime_days: int):
        self.repo = repo
        self.lifetime_days = session_lifetime_days

    def _generate_token(self) -> str:
        return secrets.token_urlsafe(32)

    async def get_or_create_session(self, token: str | None) -> BrowserSession:
        if token:
            session = await self.repo.get_by_token(token)
            if session and not session.is_expired():
                session.refresh(self.lifetime_days)
                await self.repo.update(session)
                return session  # Need to update the cookie

        # Creating a new one if there is no token or it is not relevant
        now = datetime.now(timezone.utc)
        new_session = BrowserSession(
            token=self._generate_token(),
            created_at=now,
            last_seen_at=now,
            expires_at=now + timedelta(days=self.lifetime_days)
        )
        await self.repo.create(new_session)
        return new_session
