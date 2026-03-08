from app.models import Location, Exhibition, Event, EventOccurrence


def exhibition(
        name="Test Exhibition",
        description="A test exhibition",
        artist="Test Artist",
        artist_page_url="http://example.com/artist",
        image_path="/path/to/image.jpg",
        location_id=None
):
    return Exhibition(
        name=name,
        description=description,
        artist=artist,
        artist_page_url=artist_page_url,
        image_path=image_path,
        location_id=location_id,
    )


def location(
        name="Test Location",
        subtitle="A test location",
        address="Example Avenue 123",
        phone="123-456-7890",
        email="email@email.com",
        latitude=48.8566,
        longitude=2.3522,
        original_page_url="http://example.com/location",
        image_path="/path/to/location_image.jpg",
        links=["http://example.com/link1", "http://example.com/link2"],
        bike_tour=1
):
    return Location(
        name=name,
        subtitle=subtitle,
        latitude=latitude,
        longitude=longitude,
        address=address,
        phone=phone,
        email=email,
        original_page_url=original_page_url,
        image_path=image_path,
        links=links,
        bike_tour=bike_tour
    )

def event(
        name="Test Event",
        description="A test event",
        location_id=None,
        payment_type="free",
        entry_price=None,
        booking_required=False,
        organizer="Test Organizer"
):
    return Event(
        name=name,
        description=description,
        location_id=location_id,
        payment_type=payment_type,
        entry_price=entry_price,
        booking_required=booking_required,
        organizer=organizer
    )

def event_occurrence(
        event_id=None,
        start_datetime="2024-07-01T10:00:00",
        is_cancelled=False
):
    return EventOccurrence(
        event_id=event_id,
        start_datetime=start_datetime,
        is_cancelled=is_cancelled
    )