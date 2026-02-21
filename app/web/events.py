from typing import Optional, Literal
from datetime import date
from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select, or_, and_, func
from datetime import datetime

from app.core.database import get_session
from app.models.event import Event, EventOccurrence
from app.models.location import Location
from app.core.config import settings
# from app.services.embedding import get_embedding

router = APIRouter(prefix="/events", tags=["events"])
templates = Jinja2Templates(directory="templates")


@router.get("", response_class=HTMLResponse)
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


@router.get("/list", response_class=HTMLResponse)
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
    show_cancelled: Optional[Literal["", "only", "hide"]] = None,
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
        # search_embedding = get_embedding(search).tolist()
        search_filter = or_(
            # Event.embedding.cosine_distance(search_embedding) < 0.35,
            Event.name.ilike(f"%{search}%"),
            Event.description.ilike(f"%{search}%")
        )
        filters.append(search_filter)

    if payment_types and len(payment_types) > 0:
        filters.append(Event.payment_type.in_(payment_types))

    if location_id:
        filters.append(Event.location_id == location_id)

    if show_cancelled == "only":
        filters.append(EventOccurrence.is_cancelled == True) #noqa

    if show_cancelled == "hide":
        filters.append(EventOccurrence.is_cancelled == False) #noqa

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
    event_ids = set()

    for occurrence, event, location in results:
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