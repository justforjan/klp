from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, StreamingResponse
from sqlmodel import Session, select
from datetime import datetime

from app.core.database import get_session
from app.models.event import Event, EventOccurrence
from app.models.location import Location
from app.models.exhibition import Exhibition
from app.services.pdf_generator import generate_favorites_pdf

router = APIRouter(prefix="/favourites", tags=["favourites"])


@router.get("/events")
async def get_favourite_events(
    ids: str = Query(...),
    session: Session = Depends(get_session),
):
    events_by_date = get_favourite_events_data(ids, session)
    return JSONResponse(events_by_date)


@router.get("/pdf")
async def export_favourites_pdf(
    ids: str = Query(default=""),
    exhibition_ids: str = Query(default=""),
    session: Session = Depends(get_session),
):
    events_by_date = {}
    exhibitions_by_location = {}

    if ids:
        events_by_date = get_favourite_events_data(ids, session)

    if exhibition_ids:
        try:
            exhibition_id_list = [int(id_str) for id_str in exhibition_ids.split(',') if id_str.strip()]
            if exhibition_id_list:
                query = (
                    select(Exhibition, Location)
                    .join(Location, Exhibition.location_id == Location.id)
                    .where(Exhibition.id.in_(exhibition_id_list))
                    .order_by(Location.name.asc(), Exhibition.name.asc())
                )
                results = session.exec(query).all()

                for exhibition, location in results:
                    location_key = f"{location.id}"
                    if location_key not in exhibitions_by_location:
                        exhibitions_by_location[location_key] = {
                            "location": {
                                "id": location.id,
                                "name": location.name,
                                "subtitle": location.subtitle,
                            },
                            "exhibitions": []
                        }

                    exhibitions_by_location[location_key]["exhibitions"].append({
                        "id": exhibition.id,
                        "name": exhibition.name,
                        "description": exhibition.description,
                        "artist": exhibition.artist,
                        "artist_page_url": exhibition.artist_page_url,
                    })
        except ValueError:
            pass

    if not events_by_date and not exhibitions_by_location:
        return JSONResponse({"error": "No favorites found"}, status_code=404)

    pdf_buffer = generate_favorites_pdf(events_by_date, exhibitions_by_location)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=favoriten_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        }
    )


def get_favourite_events_data(ids: str, session: Session):
    if not ids:
        return {}

    try:
        occurrence_ids = [int(id_str) for id_str in ids.split(',') if id_str.strip()]
    except ValueError:
        return {}

    if not occurrence_ids:
        return {}

    query = (
        select(EventOccurrence, Event, Location)
        .join(Event, EventOccurrence.event_id == Event.id)
        .join(Location, Event.location_id == Location.id)
        .where(EventOccurrence.id.in_(occurrence_ids))
        .order_by(EventOccurrence.start_datetime.asc())
    )
    results = session.exec(query).all()

    events_by_date = {}
    for occurrence, event, location in results:
        event_date = occurrence.start_datetime.date().isoformat()
        if event_date not in events_by_date:
            events_by_date[event_date] = []

        events_by_date[event_date].append({
            "occurrence": {
                "id": occurrence.id,
                "start_datetime": occurrence.start_datetime.isoformat(),
                "is_cancelled": occurrence.is_cancelled,
            },
            "event": {
                "name": event.name,
                "description": event.description,
                "payment_type": event.payment_type,
                "entry_price": float(event.entry_price) if event.entry_price else None,
                "material_cost": float(event.material_cost) if event.material_cost else None,
                "booking_required": event.booking_required,
                "organizer": event.organizer,
            },
            "location": {
                "id": location.id,
                "name": location.name,
                "subtitle": location.subtitle,
                "address": location.address,
                "phone": location.phone,
                "email": location.email,
            }
        })

    return events_by_date

@router.get("/exhibitions")
async def get_favourite_exhibitions(
    ids: str = Query(...),
    session: Session = Depends(get_session),
):
    if not ids:
        return JSONResponse({})

    try:
        exhibition_ids = [int(id_str) for id_str in ids.split(',') if id_str.strip()]
    except ValueError:
        return JSONResponse({})

    if not exhibition_ids:
        return JSONResponse({})

    query = (
        select(Exhibition, Location)
        .join(Location, Exhibition.location_id == Location.id)
        .where(Exhibition.id.in_(exhibition_ids))
        .order_by(Location.name.asc(), Exhibition.name.asc())
    )
    results = session.exec(query).all()

    exhibitions_by_location = {}
    for exhibition, location in results:
        location_key = f"{location.id}"
        if location_key not in exhibitions_by_location:
            exhibitions_by_location[location_key] = {
                "location": {
                    "id": location.id,
                    "name": location.name,
                    "subtitle": location.subtitle,
                },
                "exhibitions": []
            }

        exhibitions_by_location[location_key]["exhibitions"].append({
            "id": exhibition.id,
            "name": exhibition.name,
            "description": exhibition.description,
            "artist": exhibition.artist,
            "artist_page_url": exhibition.artist_page_url,
            "image_path": exhibition.image_path,
        })

    return JSONResponse(exhibitions_by_location)