import httpx
from bs4 import BeautifulSoup
from datetime import datetime, time, date, timedelta
from decimal import Decimal
from sqlmodel import Session, select
from app.core.database import engine
from app.models.event import Event, EventOccurrence
from app.models.location import Location
from app.models.bike_tour import BikeTour
import re
from typing import Optional

from app.core.config import settings



BASE_URL = "https://www.kulturelle-landpartie.de"


async def run_initial_import():
    print("Starting data import from kulturelle-landpartie.de...")

    all_events_data = []

    async with httpx.AsyncClient() as client:
        dates = generate_event_dates()

        for date_str in dates:
            print(f"Scraping events for {date_str}...")
            try:
                events = await scrape_events_for_date(client, date_str)
                all_events_data.extend(events)
            except Exception as e:
                print(f"Error scraping events for {date_str}: {e}")

    print(f"Scraped {len(all_events_data)} events. Starting batch insert...")
    batch_insert_events(all_events_data)
    print("Data import completed")


def generate_event_dates() -> list[str]:
    dates = []

    start = date.fromisoformat(settings.start_date)
    end = date.fromisoformat(settings.end_date)

    duration = (end - start) + timedelta(days=1)

    for i in range(duration.days):
        day = start + timedelta(days=i)
        dates.append(day.strftime("%d-%m"))

    return dates


async def scrape_events_for_date(client: httpx.AsyncClient, date_str: str):
    url = f"{BASE_URL}/termine/{date_str}.html"

    try:
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
    except httpx.HTTPStatusError:
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    event_rows = soup.select('.row')

    events_data = []
    for row in event_rows:
        try:
            event_data = parse_event_row(row, date_str)
            if event_data:
                events_data.append(event_data)
        except Exception as e:
            print(f"Error parsing event row: {e}")

    return events_data


def parse_event_row(row, date_str: str):
    divs = row.find_all('div', recursive=False)
    if len(divs) < 3:
        return None

    time_div = divs[0]
    content_div = divs[1]
    location_div = divs[2]

    time_str = extract_time(time_div)
    if not time_str:
        return None

    location_name, location_slug = extract_location(location_div)
    if not location_name or not location_slug:
        return None

    event_name, description = extract_event_details(content_div)
    if not event_name:
        return None

    payment_type, entry_price, material_cost = extract_payment_info(description)
    booking_required = "anmeld" in description.lower() or "buchung" in description.lower()
    organizer = extract_organizer(location_div)

    event_datetime = parse_datetime(date_str, time_str)

    return {
        'event_name': event_name,
        'description': description,
        'location_name': location_name,
        'location_slug': location_slug,
        'payment_type': payment_type,
        'entry_price': entry_price,
        'material_cost': material_cost,
        'booking_required': booking_required,
        'organizer': organizer,
        'start_datetime': event_datetime,
    }


def extract_time(div) -> Optional[str]:
    nobr = div.find('nobr')
    if nobr:
        return nobr.get_text(strip=True)
    text = div.get_text(strip=True)
    time_match = re.search(r'\d{1,2}:\d{2}', text)
    if time_match:
        return time_match.group()
    return None


def extract_location(div) -> tuple[Optional[str], Optional[str]]:
    link = div.find('a', href=re.compile(r'/orte/'))
    if link:
        location_name = link.get_text(strip=True)
        href = link.get('href', '')
        slug_match = re.search(r'/orte/(.+?)\.html', href)
        location_slug = slug_match.group(1) if slug_match else None
        return location_name, location_slug
    return None, None


def extract_event_details(div) -> tuple[Optional[str], str]:
    bold = div.find('b')
    if not bold:
        return None, ""

    event_name = bold.get_text(strip=True)

    bold.extract()
    description = div.get_text(separator=' ', strip=True)

    return event_name, description


def extract_payment_info(description: str) -> tuple[str, Optional[Decimal], Optional[Decimal]]:
    description_lower = description.lower()

    if "eintritt frei" in description_lower or "kostenfrei" in description_lower:
        return "free", None, None

    if "hutkasse" in description_lower:
        material_match = re.search(r'(\d+(?:,\d+)?)\s*€\s*mat', description_lower)
        if material_match:
            material_cost = Decimal(material_match.group(1).replace(',', '.'))
            return "hat_plus_materials", None, material_cost
        return "hat_collection", None, None

    price_match = re.search(r'eintritt.*?(\d+(?:,\d+)?)\s*€', description_lower)
    if price_match:
        price = Decimal(price_match.group(1).replace(',', '.'))
        return "fixed_price", price, None

    return "free", None, None


def extract_organizer(div) -> Optional[str]:
    text = div.get_text(strip=True)
    organizer_match = re.search(r'\(([^)]+)\)$', text)
    if organizer_match:
        return organizer_match.group(1)
    return None


def parse_datetime(date_str: str, time_str: str) -> datetime:
    day, month = date_str.split('-')
    year = settings.year
    hour, minute = time_str.split(':')

    return datetime(
        year=year,
        month=int(month),
        day=int(day),
        hour=int(hour),
        minute=int(minute)
    )


def batch_insert_events(events_data: list[dict]):
    with Session(engine) as session:
        location_map = {}
        event_map = {}

        locations = []
        for event_data in events_data:
            location_name = event_data['location_name']
            if location_name not in location_map:
                location = Location(
                    name=location_name,
                    address=f"Location address for {event_data['location_slug']}",
                    latitude=0.0,
                    longitude=0.0,
                )
                locations.append(location)
                location_map[location_name] = location

        session.add_all(locations)
        session.flush()

        events = []
        for event_data in events_data:
            location = location_map[event_data['location_name']]
            event_key = (event_data['event_name'], location.id)

            if event_key not in event_map:
                event = Event(
                    name=event_data['event_name'],
                    description=event_data['description'],
                    location_id=location.id,
                    payment_type=event_data['payment_type'],
                    entry_price=event_data['entry_price'],
                    material_cost=event_data['material_cost'],
                    booking_required=event_data['booking_required'],
                    organizer=event_data['organizer'],
                )
                events.append(event)
                event_map[event_key] = event

        session.add_all(events)
        session.flush()

        occurrences = []
        for event_data in events_data:
            location = location_map[event_data['location_name']]
            event = event_map[(event_data['event_name'], location.id)]

            occurrence = EventOccurrence(
                event_id=event.id,
                start_datetime=event_data['start_datetime'],
            )
            occurrences.append(occurrence)

        session.add_all(occurrences)
        session.commit()

        print(f"Inserted {len(locations)} locations, {len(events)} events, {len(occurrences)} occurrences")
