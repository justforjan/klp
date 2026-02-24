from testcontainers.postgres import PostgresContainer
import pytest
import os
from datetime import datetime
from sqlalchemy import delete

from app.api.favourites import get_favourite_events_data
from app.config import LocalTestSettings
from app.core.database import init_engine, run_migrations, get_session_ctx
from app.models import Exhibition
from app.models.event import Event, EventOccurrence
from app.models.location import Location

os.environ.setdefault('DOCKER_HOST', 'unix:///var/run/docker.sock')


class TestFavouritesWithTestContainer:

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request):
        postgres = PostgresContainer("pgvector/pgvector:pg17")
        postgres.start()

        def remove_container():
            postgres.stop()

        request.addfinalizer(remove_container)

        settings = LocalTestSettings().model_copy(
                update={
                    "database_host": postgres.get_container_host_ip(),
                    "database_port": postgres.get_exposed_port(5432),
                    "database_username": postgres.username,
                    "database_password": postgres.password,
                    "database_name": postgres.dbname,
                }
        )

        init_engine(settings)
        run_migrations(settings)

    @pytest.fixture(scope="function", autouse=True)
    def cleanup_database(self):
        print("cleanup_database called")
        yield
        with get_session_ctx() as session:
            session.execute(delete(EventOccurrence))
            session.execute(delete(Event))
            session.execute(delete(Location))
            session.execute(delete(Exhibition))
            session.commit()

    def test_get_favourite_event_data_should_return_empty_dict_for_no_ids(self):
        # Given
        occurrence_ids = []

        # When
        with get_session_ctx() as session:
            result = get_favourite_events_data(occurrence_ids, session)

        # Then
        assert result == {}

    def test_get_favourite_event_data_should_return_correct_favourite_event(self):

        # Given
        location_id = None
        occurrence_id = None

        with get_session_ctx() as session:
            location = Location(
                name="Museum XYZ",
                subtitle="Contemporary Art",
                latitude=52.52,
                longitude=13.405,
                address="Test Street 123"
            )
            session.add(location)
            session.commit()
            session.refresh(location)
            location_id = location.id

            event = Event(
                name="Art Workshop",
                description="Learn painting",
                location_id=location_id,
                payment_type="paid",
                entry_price=15.50,
                booking_required=True
            )
            session.add(event)
            session.commit()
            session.refresh(event)
            event_id = event.id

            occurrence = EventOccurrence(
                event_id=event_id,
                start_datetime=datetime(2024, 3, 15, 14, 30),
                is_cancelled=False
            )
            session.add(occurrence)
            session.commit()
            session.refresh(occurrence)
            occurrence_id = occurrence.id

        # When
        with get_session_ctx() as session:
            result = get_favourite_events_data([occurrence_id], session)

        # Then
        expected = {
            "2024-03-15": [
                {
                    "occurrence": {
                        "id": occurrence_id,
                        "start_datetime": "2024-03-15T14:30:00",
                        "is_cancelled": False,
                    },
                    "event": {
                        "name": "Art Workshop",
                        "description": "Learn painting",
                        "payment_type": "paid",
                        "entry_price": 15.50,
                        "material_cost": None,
                        "booking_required": True,
                        "organizer": None,
                    },
                    "location": {
                        "id": location_id,
                        "name": "Museum XYZ",
                        "subtitle": "Contemporary Art",
                        "address": "Test Street 123",
                        "phone": None,
                        "email": None,
                    }
                }
            ]}

        assert result == expected

    def test_get_favourite_event_data_should_return_empty_dict_if_favourites_do_not_exist(self):

        # Given
        non_existent_occurrence_id = 1

        # When
        with get_session_ctx() as session:
            result = get_favourite_events_data([non_existent_occurrence_id], session)

        # Then
        assert result == {}





