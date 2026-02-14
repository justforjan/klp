from sqlmodel import create_engine, Session, SQLModel
from app.core.config import settings
from alembic import command
from alembic.config import Config
import os

def run_migrations(reset: bool = False):
    alembic_cfg = Config("alembic.ini")

    if reset:
        assert os.getenv("ENV") != "prod", "Cannot reset DB in production!"
        command.downgrade(alembic_cfg, "base")

    command.upgrade(alembic_cfg, "head")


engine = create_engine(settings.database_url, echo=False)


def get_session():
    with Session(engine) as session:
        yield session
