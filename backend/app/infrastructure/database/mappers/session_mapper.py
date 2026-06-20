from app.domain.entities import BrowserSession
from app.infrastructure.database.models.browser_session_model import BrowserSessionORM


def to_domain(orm: BrowserSessionORM) -> BrowserSession:
    return BrowserSession(
        id=orm.id,
        token=orm.token,
        created_at=orm.created_at,
        last_seen_at=orm.last_seen_at,
        expires_at=orm.expires_at,
    )


def to_orm(domain: BrowserSession) -> BrowserSessionORM:
    return BrowserSessionORM(
        id=domain.id,
        token=domain.token,
        created_at=domain.created_at,
        last_seen_at=domain.last_seen_at,
        expires_at=domain.expires_at,
    )
