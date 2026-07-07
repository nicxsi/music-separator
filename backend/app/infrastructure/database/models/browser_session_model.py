import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from app.infrastructure.database.models.job_model import JobORM

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class BrowserSessionORM(Base):
    """
    Anonymous browser session
    The browser receives a cookie containing a random token
    It can be expanded to a complete authorization system
    """

    __tablename__ = "browser_sessions"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    token: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )

    jobs: Mapped[list["JobORM"]] = relationship(
        back_populates="session"
    )
