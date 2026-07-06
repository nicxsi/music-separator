from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from app.infrastructure.database.models.browser_session_model import (
        BrowserSessionORM,
    )
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class JobORM(Base):
    __tablename__ = "jobs"

    # The ID is generated in the domain entity
    id: Mapped[UUID] = mapped_column(primary_key=True)

    # ID of the anonymous usage session
    session_id: Mapped[UUID] = mapped_column(
        ForeignKey("browser_sessions.id"),
        nullable=False,
        index=True
    )

    filename: Mapped[str] = mapped_column(String)

    status: Mapped[str] = mapped_column(String)

    error: Mapped[str | None] = mapped_column(String, nullable=True)

    session: Mapped["BrowserSessionORM"] = relationship(back_populates="jobs")
