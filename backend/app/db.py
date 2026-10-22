"""Database setup: engine, session and tables (SQLAlchemy 2 style)."""

from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy import JSON, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from app.config import get_settings

settings = get_settings()

# pool_pre_ping: checks the connection is alive before using it
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Analysis(Base):
    """One saved run of the Criteria Analyzer."""

    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(300), default="Untitled")
    source_text: Mapped[str] = mapped_column(Text)
    result: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


def init_db() -> None:
    # Simple for a prototype. Later: switch to Alembic migrations.
    Base.metadata.create_all(bind=engine)


def get_session() -> Iterator[Session]:
    """FastAPI dependency: one DB session per request, always closed."""
    with SessionLocal() as session:
        yield session


# Reusable type: write `session: SessionDep` in any route to get a DB session.
SessionDep = Annotated[Session, Depends(get_session)]
