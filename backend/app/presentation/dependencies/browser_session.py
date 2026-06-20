from app.application.services.session_service import BrowserSessionService
from app.core.config import settings
from app.domain.entities import BrowserSession
from app.infrastructure.database.deps import get_db
from app.infrastructure.repositories.session_repository import BrowserSessionRepository
from fastapi import Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=token,
        # The max_age parameter in response.set_cookie() accepts the cookie
        # lifetime in seconds, not days, according to the HTTP standard
        max_age=settings.SESSION_LIFETIME_DAYS * 24 * 60 * 60,
        # With httponly the token will be unavailable to
        # JavaScript (protection against XSS attacks)
        httponly=True,
        # samesite determines when the browser should send cookies
        # automatically (protection against CSRF attacks)
        samesite="lax",
        secure=settings.COOKIE_SECURE,
        path="/",
    )

async def get_browser_session(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> BrowserSession:
    # Infrastructure assembly (in a DI container)
    repo = BrowserSessionRepository(session=db)
    service = BrowserSessionService(
        repo=repo,
        session_lifetime_days=settings.SESSION_LIFETIME_DAYS
    )

    # Get a token from a cookie
    raw_token = request.cookies.get(settings.SESSION_COOKIE_NAME)

    # Calling the domain logic
    session = await service.get_or_create_session(raw_token)

    # If the session is new or updated, write a cookie in the HTTP Response
    _set_session_cookie(response, session.token)
    return session
