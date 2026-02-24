from testcontainers.postgres import PostgresContainer
import pytest
import os
from datetime import datetime

from app.api.favourites import get_favourite_events_data
from app.config import LocalTestSettings
from app.core.database import init_engine, run_migrations, get_session_ctx
from app.models.event import Event, EventOccurrence
from app.models.location import Location

os.environ.setdefault('DOCKER_HOST', 'unix:///var/run/docker.sock')


def test_get_favourite_event_data_should_return_empty_dict_for_no_ids():
    # Given
    occurrence_ids = []

    # When
    result = get_favourite_events_data(occurrence_ids, None)

    # Then
    assert result == {}


class TestFavouritesWithTestContainer:

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request):
        postgres = PostgresContainer("postgres:17-alpine")
        postgres.start()

        def remove_container():
            postgres.stop()

        request.addfinalizer(remove_container)

        settings = LocalTestSettings().model_copy(
                update={
                    "database_host": postgres.get_container_host_ip(),
                    "database_port": postgres.get_exposed_port(5433),
                    "database_username": postgres.username,
                    "database_password": postgres.password,
                    "database_name": postgres.dbname,
                }
        )

        init_engine(settings)
        run_migrations(reset=True)

    def test_get_favourite_event_data_should_return_correct_favourite_event(self):

        # Given
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

            event = Event(
                name="Art Workshop",
                description="Learn painting",
                location_id=location.id,
                payment_type="paid",
                entry_price=15.50,
                booking_required=True
            )
            session.add(event)
            session.commit()
            session.refresh(event)

            occurrence = EventOccurrence(
                event_id=event.id,
                start_datetime=datetime(2024, 3, 15, 14, 30),
                is_cancelled=False
            )
            session.add(occurrence)
            session.commit()
            session.refresh(occurrence)

        # When
        with get_session_ctx() as session:
            result = get_favourite_events_data([occurrence.id], session)

        # Then
        assert "2024-03-15" in result
        event_data = result["2024-03-15"][0]
        assert event_data["event"]["name"] == "Art Workshop"
        assert event_data["event"]["entry_price"] == 15.50
        assert event_data["event"]["booking_required"] is True
        assert event_data["location"]["address"] == "Test Street 123"





