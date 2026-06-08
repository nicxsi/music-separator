from uuid import UUID

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class JobORM(Base):
    __tablename__ = "jobs"

    # The ID is generated in the domain entity
    id: Mapped[UUID] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    error: Mapped[str | None] = mapped_column(String, nullable=True)
