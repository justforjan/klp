from sqlmodel import create_engine, Session
from sqlalchemy import Engine
from alembic import command
from alembic.config import Config
import os
import sys
from contextlib import contextmanager

from app.config import AppSettings

def run_migrations(reset: bool = False):
    alembic_cfg = Config("alembic.ini")

    if reset:
        assert os.getenv("ENV") != "prod", "Cannot reset DB in production!"
        try:
            command.downgrade(alembic_cfg, "base")
        except Exception as exc:
            sys.exit(f"Failed to downgrade database during reset: {exc}")

    try:
        command.upgrade(alembic_cfg, "head")
    except Exception as exc:
        sys.exit(f"Failed to run alembic migrations: {exc}")

_engine: Engine | None = None

def init_engine(settings: AppSettings) -> None:
    global _engine
    _engine = create_engine(
        f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_host}:{settings.database_port}/{settings.database_name}",
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
    )

def get_engine() -> Engine:
    assert _engine is not None, "Engine not initialized. Call init_engine() at startup."
    return _engine


def get_session():
    with Session(get_engine()) as session:
        yield session


@contextmanager
def get_session_ctx():
    with Session(get_engine()) as session:
        yield session

