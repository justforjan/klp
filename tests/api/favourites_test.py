
from app.api.favourites import get_favourite_events_data


def test_get_favourite_event_data_should_return_empty_dict_for_no_ids():
    # Given
    occurrence_ids = []

    # When
    result = get_favourite_events_data(occurrence_ids, None)

    # Then
    assert result == {}

# postgres = PostgresContainer("postgres:17-alpine")
# @pytest.ignore(reason="Requires test container setup")
# class TestFavouritesWithTestContainer:
#
#     @pytest.fixture(scope="class", autouse=True)
#     def setup(self, request):
#         postgres.start()
#
#         def remove_container():
#             postgres.stop()
#
#         request.addfinalizer(remove_container)
#         os.environ["DB_CONN"] = postgres.get_connection_url()
#         os.environ["DATABASE_HOST"] = postgres.get_container_host_ip()
#         os.environ["DATABASE_PORT"] = postgres.get_exposed_port(5432)
#         os.environ["DATABASE_USERNAME"] = postgres.username
#         os.environ["DATABASE_PASSWORD"] = postgres.password
#         os.environ["DATABASE_NAME"] = postgres.dbname
#
#
#     def test_get_favourite_event_data_should_return_empty_dict_for_invalid_ids(self):
#         assert True




