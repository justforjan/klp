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
from pathlib import Path

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

        print("Starting location details scraping...")
        await scrape_all_location_details(client)

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
            location_slug = event_data['location_slug']
            if location_name not in location_map:
                original_page_url = f"{BASE_URL}/orte/{location_slug}.html" if location_slug else None
                location = Location(
                    name=location_name,
                    latitude=0.0,
                    longitude=0.0,
                    original_page_url=original_page_url,
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


async def scrape_all_location_details(client: httpx.AsyncClient):
    static_dir = Path("static/locations")
    static_dir.mkdir(parents=True, exist_ok=True)

    with Session(engine) as session:
        locations = session.exec(select(Location)).all()

        for location in locations:
            if not location.original_page_url:
                continue

            print(f"Scraping details for {location.name}...")
            try:
                details = await scrape_location_details(client, location)
                if details:
                    if 'subtitle' in details:
                        location.subtitle = details['subtitle']
                    if 'address' in details:
                        location.address = details['address']
                    if 'phone' in details:
                        location.phone = details['phone']
                    if 'email' in details:
                        location.email = details['email']
                    if 'links' in details:
                        location.links = details['links']

                    session.add(location)
                    session.commit()

                    if 'image_url' in details:
                        location_slug = location.original_page_url.split('/')[-1].replace('.html', '') if location.original_page_url else f"location_{location.id}"

                        image_url_path = details['image_url'].split('?')[0]
                        image_ext = Path(image_url_path).suffix or '.jpg'
                        expected_filename = f"{location_slug}{image_ext}"
                        expected_filepath = static_dir / expected_filename

                        if expected_filepath.exists():
                            print(f"Image already exists for {location.name} at {expected_filepath}, skipping download")
                            if not location.image_path:
                                location.image_path = f"/static/locations/{expected_filename}"
                                session.add(location)
                                session.commit()
                        else:
                            print(f"Downloading image for {location.name}...")
                            image_path = await download_location_image(client, details['image_url'], location_slug)
                            if image_path:
                                location.image_path = image_path
                                session.add(location)
                                session.commit()
                                print(f"Downloaded image for {location.name}")
                            else:
                                print(f"Failed to download image for {location.name}")
            except Exception as e:
                print(f"Error scraping location details for {location.name}: {e}")
                session.rollback()


async def download_location_image(client: httpx.AsyncClient, image_url: str, location_slug: str) -> Optional[str]:
    try:
        if not image_url.startswith('http'):
            image_url = f"{BASE_URL}{image_url}"

        response = await client.get(image_url, timeout=10.0)
        response.raise_for_status()

        static_dir = Path("static/locations")
        static_dir.mkdir(parents=True, exist_ok=True)

        image_ext = Path(image_url.split('?')[0]).suffix or '.jpg'
        image_filename = f"{location_slug}{image_ext}"
        image_path = static_dir / image_filename

        with open(image_path, 'wb') as f:
            f.write(response.content)

        return f"/static/locations/{image_filename}"
    except Exception as e:
        print(f"Error downloading image from {image_url}: {e}")
        return None


async def scrape_location_details(client: httpx.AsyncClient, location: Location) -> dict:
    try:
        response = await client.get(location.original_page_url, timeout=10.0)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching {location.original_page_url}: {e}")
        return {}

    soup = BeautifulSoup(response.text, 'html.parser')
    data = {}

    h3 = soup.find('h3')
    if h3:
        data['subtitle'] = h3.get_text(strip=True)

    comblock = soup.find('div', id='comblock')
    if not comblock:
        return data

    img_div = comblock.find('div', class_='img')
    if img_div:
        img_tag = img_div.find('img')
        if img_tag and img_tag.get('src'):
            data['image_url'] = img_tag.get('src')

    all_mailto_links = comblock.find_all('a', href=re.compile(r'^mailto:'))
    email = None
    for mailto_link in all_mailto_links:
        href = mailto_link.get('href', '')
        email_from_href = href.replace('mailto:', '').strip()
        if '@' in email_from_href:
            email = email_from_href
            break

    paragraphs = comblock.find_all('p')
    address_parts = []
    phone = None
    links = []

    for i, p in enumerate(paragraphs):
        text = p.get_text(strip=True)

        phone_match = re.search(r'Fon\s+(\+?[\d\s-]+)', text, re.IGNORECASE)
        if phone_match:
            phone = phone_match.group(1).strip()
            continue

        web_links = p.find_all('a', target='_blank')
        for link in web_links:
            href = link.get('href', '')
            if href and not href.startswith('mailto:'):
                links.append(href)

        if web_links or phone_match:
            continue

        if i > 0 and '<br' in str(p).lower():
            br_parts = []
            for content in p.stripped_strings:
                if content and len(content) > 2:
                    br_parts.append(content)

            if len(br_parts) >= 2:
                for part in br_parts:
                    if '&' not in part and not any(x in part.lower() for x in ['fon', 'mail', 'e.v.', 'gbr']):
                        address_parts.append(part)

    if address_parts:
        data['address'] = ', '.join(address_parts[:2])

    if phone:
        data['phone'] = phone
    if email:
        data['email'] = email
    if links:
        data['links'] = links

    return data
