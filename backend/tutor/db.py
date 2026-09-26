"""Conexión a PostgreSQL con SQLAlchemy 2."""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from tutor.config import get_settings


class Base(DeclarativeBase):
    """Base de los modelos ORM; Alembic la usa para comparar el esquema."""


engine = create_engine(get_settings().database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_session() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session
