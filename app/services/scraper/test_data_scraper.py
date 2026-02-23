from typing import override
from sqlmodel import Session
from datetime import datetime

from app.services.scraper.base import BaseScraper
from app.models import Location, Event, Exhibition, EventOccurrence
from app.core.database import engine

class TestDataScraper(BaseScraper):

    @override
    async def run_initial_import(self) -> None:
        print("Running initial import for test data")

        # Locations
        location1 = Location(
            id = 1,
            name="Test Location 1",
            address="123 Test St, Test City",
            latitude=0,
            longitude=0,
            phone_number="0123456789",
            bike_tour=1
        )
        location2 = Location(
            id = 2,
            name="Test Location 2",
            address="456 Sample Ave, Sample Town",
            latitude=34.0522,
            longitude=-118.2437,
            email="email@test-location2.com",
            links=["http://www.testlocation2.com", "http://www.testlocation2.com/events"],
            bike_tour=2,
        )

        # Events
        event1 = Event(
            id = 1,
            name="Test Event 1",
            description="This is a test event.",
            location_id=1,
            payment_type="free"
        )
        event2 = Event(
            id = 2,
            name="Test Event 2",
            description="This is another test event.",
            location_id=2,
            payment_type=""
        )

        # Exhibitions
        exhibition1 = Exhibition(
            id = 1,
            name="Test Exhibition 1",
            description="This is a test exhibition.",
            artist="Test Artist",
            location_id=1,
        )

        # Event Occurrences
        event_occurrence1 = EventOccurrence(
            id = 1,
            event_id=1,
            start_datetime=datetime.fromisoformat("2024-07-01T10:00:00"),
            is_cancelled=False
        )
        event_occurrence2 = EventOccurrence(
            id = 2,
            event_id=1,
            start_datetime=datetime.fromisoformat("2024-07-02T10:00:00"),
            is_cancelled=True
        )
        event_occurrence3 = EventOccurrence(
            id = 3,
            event_id=2,
            start_datetime=datetime.fromisoformat("2024-07-02T14:00:00"),
            is_cancelled=False
        )

        with Session(engine) as session:
            session.add_all([location1, location2, event1, event2, exhibition1, event_occurrence1, event_occurrence2, event_occurrence3])
            session.commit()

