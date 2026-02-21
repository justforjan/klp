from sqlmodel import create_engine, Session, SQLModel
from app.core.config import settings
from alembic import command
from alembic.config import Config
import os
import sys

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

database_url = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_host}:{settings.database_port}/{settings.database_name}"
engine = create_engine(database_url, echo=False)


def get_session():
    with Session(engine) as session:
        yield session
