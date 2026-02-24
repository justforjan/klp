from sqlmodel import create_engine, Session
from sqlalchemy import Engine
from alembic import command
from alembic.config import Config
import os
from pathlib import Path
from contextlib import contextmanager

from app.config import AppSettings

def run_migrations(settings: AppSettings):

    project_root = Path(__file__).resolve().parents[2]
    alembic_ini_path = project_root / "alembic.ini"

    alembic_cfg = Config(str(alembic_ini_path))
    alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)

    if settings.reload_data:
        assert os.getenv("ENV") != "prod", "Cannot reset DB in production!"
        try:
            command.downgrade(alembic_cfg, "base")
        except Exception as exc:
            raise RuntimeError(f"Failed to downgrade database during reset: {exc}") from exc

    try:
        command.upgrade(alembic_cfg, "head")
    except Exception as exc:
        raise RuntimeError(f"Failed to run alembic migrations: {exc}") from exc

_engine: Engine | None = None

def init_engine(settings: AppSettings) -> None:
    global _engine
    _engine = create_engine(
        settings.database_url,
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

