from typing import Optional
from datetime import date
from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select, and_
from datetime import datetime

from app.core.database import get_session
from app.models.event import Event, EventOccurrence
from app.models.location import Location
from app.models.exhibition import Exhibition
from app.config import settings

router = APIRouter(prefix="/locations", tags=["locations"])
templates = Jinja2Templates(directory="templates")


@router.get("", response_class=HTMLResponse)
async def locations_page(
    request: Request,
    session: Session = Depends(get_session),
):
    query = select(Location).order_by(Location.name.asc())
    locations = session.exec(query).all()

    return templates.TemplateResponse(
        "locations.html",
        {
            "request": request,
            "locations": locations,
        },
    )


@router.get("/{location_id}", response_class=HTMLResponse)
async def location_detail_page(
    request: Request,
    location_id: int,
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    session: Session = Depends(get_session),
):
    location = session.get(Location, location_id)
    if not location:
        return templates.TemplateResponse(
            "404.html",
            {"request": request},
            status_code=404,
        )

    has_query_params = any(param is not None for param in [
        request.query_params.get('start_date'),
        request.query_params.get('end_date')
    ])

    if not has_query_params:
        start_date = settings.start_date
        end_date = settings.end_date
    else:
        start_date = start_date or ""
        end_date = end_date or ""

    parsed_start_date = None if not start_date or start_date.strip() == "" else date.fromisoformat(start_date)
    parsed_end_date = None if not end_date or end_date.strip() == "" else date.fromisoformat(end_date)

    query = (
        select(EventOccurrence, Event)
        .join(Event, EventOccurrence.event_id == Event.id)
        .where(Event.location_id == location_id)
    )

    filters = []
    if parsed_start_date:
        start_datetime = datetime.combine(parsed_start_date, datetime.min.time())
        filters.append(EventOccurrence.start_datetime >= start_datetime)

    if parsed_end_date:
        end_datetime = datetime.combine(parsed_end_date, datetime.max.time())
        filters.append(EventOccurrence.start_datetime <= end_datetime)

    if filters:
        query = query.where(and_(*filters))

    query = query.order_by(EventOccurrence.start_datetime.asc())
    results = session.exec(query).all()

    exhibitions_query = select(Exhibition).where(Exhibition.location_id == location_id)
    exhibitions = session.exec(exhibitions_query).all()

    cancellation_phrases = ["fällt aus", "fällt leider aus", "fällt weg"]

    events_by_date = {}
    for occurrence, event in results:
        is_cancelled = False
        if event.name:
            name_lower = event.name.lower()
            if any(phrase in name_lower for phrase in cancellation_phrases):
                is_cancelled = True
        if not is_cancelled and event.description:
            description_lower = event.description.lower()
            if any(phrase in description_lower for phrase in cancellation_phrases):
                is_cancelled = True

        if is_cancelled:
            occurrence.is_cancelled = True

        event_date = occurrence.start_datetime.date()
        if event_date not in events_by_date:
            events_by_date[event_date] = []

        events_by_date[event_date].append({
            "occurrence": occurrence,
            "event": event,
        })

    return templates.TemplateResponse(
        "location_detail.html",
        {
            "request": request,
            "location": location,
            "exhibitions": exhibitions,
            "events_by_date": events_by_date,
            "start_date": start_date,
            "end_date": end_date,
            "default_start_date": settings.start_date,
            "default_end_date": settings.end_date,
        },
    )
