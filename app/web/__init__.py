from typing import Optional
from datetime import date
from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select, or_, and_, func
from datetime import datetime

from app.core.database import get_session
from app.models.event import Event, EventOccurrence
from app.models.location import Location
from app.core.config import settings


router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/events", response_class=HTMLResponse)
async def events_page(
    request: Request,
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    show_cancelled: Optional[str] = Query(default=None),
    payment_types: Optional[str] = Query(default=None),
    location_id: Optional[int] = Query(default=None),
    page: int = Query(1, ge=1),
    session: Session = Depends(get_session),
):
    has_query_params = any(param is not None for param in [
        request.query_params.get('start_date'),
        request.query_params.get('end_date'),
        request.query_params.get('search'),
        request.query_params.get('show_cancelled'),
        request.query_params.get('payment_types'),
        request.query_params.get('location_id')
    ])

    if not has_query_params:
        start_date = settings.start_date
        end_date = settings.end_date
    else:
        start_date = start_date or ""
        end_date = end_date or ""

    parsed_start_date = None if not start_date or start_date.strip() == "" else date.fromisoformat(start_date)
    parsed_end_date = None if not end_date or end_date.strip() == "" else date.fromisoformat(end_date)

    payment_types_list = payment_types.split(',') if payment_types else None

    selected_location = None
    if location_id:
        selected_location = session.get(Location, location_id)

    pagination_data = get_event_occurrences(
        session,
        parsed_start_date,
        parsed_end_date,
        search,
        page,
        show_cancelled=show_cancelled,
        payment_types=payment_types_list,
        location_id=location_id
    )

    return templates.TemplateResponse(
        "events.html",
        {
            "request": request,
            "occurrences": pagination_data["occurrences"],
            "page": pagination_data["page"],
            "has_more": pagination_data["has_more"],
            "total": pagination_data["total"],
            "start_date": start_date,
            "end_date": end_date,
            "search": search or "",
            "show_cancelled": show_cancelled or "",
            "payment_types": payment_types or "",
            "location_id": location_id,
            "selected_location": selected_location,
            "default_start_date": settings.start_date,
            "default_end_date": settings.end_date,
        },
    )


@router.get("/events/list", response_class=HTMLResponse)
async def events_list_partial(
    request: Request,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    show_cancelled: Optional[str] = Query(None),
    payment_types: Optional[str] = Query(None),
    location_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    session: Session = Depends(get_session),
):
    parsed_start_date = None if not start_date or start_date.strip() == "" else date.fromisoformat(start_date)
    parsed_end_date = None if not end_date or end_date.strip() == "" else date.fromisoformat(end_date)

    payment_types_list = payment_types.split(',') if payment_types else None

    pagination_data = get_event_occurrences(
        session,
        parsed_start_date,
        parsed_end_date,
        search,
        page,
        show_cancelled=show_cancelled,
        payment_types=payment_types_list,
        location_id=location_id
    )

    return templates.TemplateResponse(
        "partials/event_list.html",
        {
            "request": request,
            "occurrences": pagination_data["occurrences"],
            "page": pagination_data["page"],
            "has_more": pagination_data["has_more"],
            "total": pagination_data["total"],
            "start_date": start_date,
            "end_date": end_date,
            "search": search,
            "show_cancelled": show_cancelled,
            "payment_types": payment_types,
            "location_id": location_id,
        },
    )


def get_event_occurrences(
    session: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    show_cancelled: Optional[str] = None,
    payment_types: Optional[list[str]] = None,
    location_id: Optional[int] = None,
):
    base_query = (
        select(EventOccurrence, Event, Location)
        .join(Event, EventOccurrence.event_id == Event.id)
        .join(Location, Event.location_id == Location.id)
    )

    filters = []

    if start_date:
        start_datetime = datetime.combine(start_date, datetime.min.time())
        filters.append(EventOccurrence.start_datetime >= start_datetime)

    if end_date:
        end_datetime = datetime.combine(end_date, datetime.max.time())
        filters.append(EventOccurrence.start_datetime <= end_datetime)

    if search and search.strip():
        search_filter = or_(
            Event.name.ilike(f"%{search}%"),
            Event.description.ilike(f"%{search}%")
        )
        filters.append(search_filter)

    if payment_types and len(payment_types) > 0:
        filters.append(Event.payment_type.in_(payment_types))

    if location_id:
        filters.append(Event.location_id == location_id)

    if filters:
        base_query = base_query.where(and_(*filters))

    count_query = (
        select(func.count(EventOccurrence.id))
        .select_from(EventOccurrence)
        .join(Event, EventOccurrence.event_id == Event.id)
        .join(Location, Event.location_id == Location.id)
    )
    if filters:
        count_query = count_query.where(and_(*filters))

    total = session.exec(count_query).one()

    data_query = base_query.order_by(EventOccurrence.start_datetime.asc())
    offset = (page - 1) * page_size
    data_query = data_query.limit(page_size).offset(offset)

    results = session.exec(data_query).all()

    occurrences = []
    cancellation_phrases = ["fällt aus", "fällt leider aus", "fällt weg"]
    event_ids = set()

    for occurrence, event, location in results:
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

        if show_cancelled == "only" and not is_cancelled:
            continue
        elif show_cancelled == "hide" and is_cancelled:
            continue

        occurrences.append({
            "occurrence": occurrence,
            "event": event,
            "location": location,
        })
        event_ids.add(event.id)

    all_occurrences_map = {}
    if event_ids:
        all_occurrences_query = (
            select(EventOccurrence)
            .where(EventOccurrence.event_id.in_(event_ids))
            .order_by(EventOccurrence.start_datetime.asc())
        )
        all_occurrences_results = session.exec(all_occurrences_query).all()

        for occ in all_occurrences_results:
            if occ.event_id not in all_occurrences_map:
                all_occurrences_map[occ.event_id] = []
            all_occurrences_map[occ.event_id].append(occ)

    for item in occurrences:
        occurrence = item["occurrence"]
        event = item["event"]
        other_occurrences = [
            occ for occ in all_occurrences_map.get(event.id, [])
            if occ.id != occurrence.id
        ]
        item["other_occurrences"] = other_occurrences

    has_more = (page * page_size) < total

    return {
        "occurrences": occurrences,
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_more": has_more,
    }


@router.get("/locations", response_class=HTMLResponse)
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


@router.get("/locations/{location_id}", response_class=HTMLResponse)
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
            "events_by_date": events_by_date,
            "start_date": start_date,
            "end_date": end_date,
            "default_start_date": settings.start_date,
            "default_end_date": settings.end_date,
        },
    )


@router.get("/favourites", response_class=HTMLResponse)
async def favourites_page(
    request: Request,
    session: Session = Depends(get_session),
):
    return templates.TemplateResponse(
        "favourites.html",
        {
            "request": request,
        },
    )


@router.get("/api/favourites/events")
async def get_favourite_events(
    ids: str = Query(...),
    session: Session = Depends(get_session),
):
    if not ids:
        return JSONResponse([])

    try:
        occurrence_ids = [int(id_str) for id_str in ids.split(',') if id_str.strip()]
    except ValueError:
        return JSONResponse([])

    if not occurrence_ids:
        return JSONResponse([])

    query = (
        select(EventOccurrence, Event, Location)
        .join(Event, EventOccurrence.event_id == Event.id)
        .join(Location, Event.location_id == Location.id)
        .where(EventOccurrence.id.in_(occurrence_ids))
        .order_by(EventOccurrence.start_datetime.asc())
    )
    results = session.exec(query).all()

    cancellation_phrases = ["fällt aus", "fällt leider aus", "fällt weg"]

    events_by_date = {}
    for occurrence, event, location in results:
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
            }
        })

    return JSONResponse(events_by_date)


@router.get("/api/locations/search")
async def search_locations(
    q: str = Query("", min_length=0),
    session: Session = Depends(get_session),
):
    if not q or len(q.strip()) == 0:
        locations = session.exec(select(Location).order_by(Location.name.asc()).limit(10)).all()
    else:
        query = (
            select(Location)
            .where(Location.name.ilike(f"%{q}%"))
            .order_by(Location.name.asc())
            .limit(20)
        )
        locations = session.exec(query).all()

    return JSONResponse([
        {"id": loc.id, "name": loc.name, "subtitle": loc.subtitle}
        for loc in locations
    ])
