from datetime import datetime
from sqlmodel import Session, select
from app.core.database import engine
from app.models import Event, EventOccurrence, Location, BikeTour, LocationBikeTour


def test_create_models():
    with Session(engine) as session:
        bike_tour = BikeTour(
            number=4,
            komoot_link="https://www.komoot.com/tour/12345"
        )
        session.add(bike_tour)

        location = Location(
            name="BANKEWITZ",
            subtitle="IM VERMEINTLICH WILDEN GARTEN",
            address="Zum Seinitz Moor 1, 29597 Stoetze OT Bankewitz",
            phone="05872 986107",
            email="keramik@wandafulworld.de",
            latitude=53.0234,
            longitude=11.1234,
            google_maps_link="https://maps.google.com/?q=53.0234,11.1234",
            links=["http://www.wandafulworld.de"]
        )
        session.add(location)
        session.flush()

        location_bike_tour = LocationBikeTour(
            location_id=location.id,
            bike_tour_id=bike_tour.id,
            order=1
        )
        session.add(location_bike_tour)

        event = Event(
            name="Bewegen am Morgen",
            description="Wir starten bewegt in den Tag. Die Mobilisierung des Körpers über sanfte Bewegungen",
            location_id=location.id,
            payment_type="hat_collection",
            booking_required=False,
            organizer="Meike Klapprodt"
        )
        session.add(event)
        session.flush()

        occurrence1 = EventOccurrence(
            event_id=event.id,
            start_datetime=datetime(2025, 5, 29, 9, 0),
            is_cancelled=False
        )
        occurrence2 = EventOccurrence(
            event_id=event.id,
            start_datetime=datetime(2025, 5, 30, 9, 0),
            is_cancelled=False
        )
        session.add(occurrence1)
        session.add(occurrence2)

        session.commit()

        print("✓ Successfully created test data")

        statement = select(Location).where(Location.name == "BANKEWITZ")
        result = session.exec(statement).first()
        print(f"✓ Found location: {result.name}")
        print(f"  - Subtitle: {result.subtitle}")
        print(f"  - Address: {result.address}")
        print(f"  - Links: {result.links}")

        statement = select(Event).where(Event.name == "Bewegen am Morgen")
        result = session.exec(statement).first()
        print(f"✓ Found event: {result.name}")
        print(f"  - Location: {result.location.name}")
        print(f"  - Organizer: {result.organizer}")
        print(f"  - Payment type: {result.payment_type}")
        print(f"  - Number of occurrences: {len(result.occurrences)}")

        for i, occ in enumerate(result.occurrences, 1):
            print(f"    {i}. {occ.start_datetime}")

        statement = select(BikeTour).where(BikeTour.number == 4)
        result = session.exec(statement).first()
        print(f"✓ Found bike tour: #{result.number}")
        print(f"  - Komoot link: {result.komoot_link}")
        print(f"  - Locations on tour: {len(result.locations)}")

        print("\n✓ All tests passed!")


if __name__ == "__main__":
    test_create_models()
