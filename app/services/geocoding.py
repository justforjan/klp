import httpx
import asyncio
import re
from urllib.parse import quote
from sqlmodel import select
from app.models.location import Location
from app.core.database import get_session_ctx


async def geocode_locations():
    print("Starting geocoding task for locations...")

    with get_session_ctx() as session:
        locations = session.exec(
            select(Location).where(
                (Location.latitude == 0.0) | (Location.longitude == 0.0)
            )
        ).all()

        if not locations:
            print("No locations need geocoding")
            return

        print(f"Found {len(locations)} locations to geocode")

        async with httpx.AsyncClient() as client:
            for location in locations:
                try:
                    cleaned = clean_address(location.address)
                    print(f"Geocoding {location.name}... (address: {location.address} -> cleaned: {cleaned})")
                    coords = await geocode_address(client, location.address)

                    if coords:
                        location.latitude = coords['lat']
                        location.longitude = coords['lon']
                        session.add(location)
                        session.commit()
                        print(f"Successfully geocoded {location.name}: {coords['lat']}, {coords['lon']}")
                    else:
                        print(f"Could not geocode {location.name}")

                    await asyncio.sleep(1)

                except Exception as e:
                    print(f"Error geocoding {location.name}: {e}")
                    session.rollback()

        print("Geocoding task completed")


def clean_address(address: str) -> str:
    cleaned = re.sub(r'\([^)]*\)', '', address)
    cleaned = re.sub(r'\bOT\b', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = cleaned.strip()
    return cleaned


async def geocode_address(client: httpx.AsyncClient, address: str) -> dict | None:
    cleaned_address = clean_address(address)
    encoded_address = quote(cleaned_address)
    url = f"https://nominatim.openstreetmap.org/search?q={encoded_address}&format=json&limit=1"

    headers = {
        'User-Agent': 'Kulturelle-Landpartie-App/1.0'
    }

    try:
        response = await client.get(url, headers=headers, timeout=10.0)
        response.raise_for_status()

        data = response.json()

        if data and len(data) > 0:
            result = data[0]

            lat = float(result['lat'])
            lon = float(result['lon'])

            if lon < 10.6 or lon > 11.7 or lat < 52.7 or lat > 53.5:
                print(f"Geocoding result for '{address}' is out of bounds: lat={lat}, lon={lon}")
                return None

            return {
                'lat': lat,
                'lon': lon
            }

        return None

    except Exception as e:
        print(f"Error fetching geocode data: {e}")
        return None
