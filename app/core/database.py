from sqlmodel import create_engine, Session, SQLModel
from app.core.config import settings

engine = create_engine(settings.database_url, echo=False)


def drop_and_create_db():
    from app.models import Event, EventOccurrence, Location, BikeTour, LocationBikeTour
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def create_db_and_tables():
    from app.models import Event, EventOccurrence, Location, BikeTour, LocationBikeTour
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
