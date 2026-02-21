from typing import Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, or_, and_
from app.core.database import get_session
from app.models.event import Event, EventOccurrence
from app.models.location import Location
from app.schemas.event import EventOccurrenceResponse, EventResponse, LocationResponse


router = APIRouter(prefix="/events", tags=["events"])

@router.get("/occurrences", response_model=list[EventOccurrenceResponse])
def list_event_occurrences(
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    search: Optional[str] = Query(None, description="Search in event name or description"),
    session: Session = Depends(get_session),
):
    query = (
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

    if search:
        search_filter = or_(
            Event.name.ilike(f"%{search}%"),
            Event.description.ilike(f"%{search}%")
        )
        filters.append(search_filter)

    if filters:
        query = query.where(and_(*filters))

    query = query.order_by(EventOccurrence.start_datetime.asc())

    results = session.exec(query).all()

    response = []
    for occurrence, event, location in results:
        response.append(
            EventOccurrenceResponse(
                id=occurrence.id,
                start_datetime=occurrence.start_datetime,
                end_datetime=occurrence.end_datetime,
                is_cancelled=occurrence.is_cancelled,
                event=EventResponse(
                    id=event.id,
                    name=event.name,
                    description=event.description,
                    payment_type=event.payment_type,
                    entry_price=event.entry_price,
                    material_cost=event.material_cost,
                    booking_required=event.booking_required,
                    organizer=event.organizer,
                ),
                location=LocationResponse(
                    id=location.id,
                    name=location.name,
                    subtitle=location.subtitle,
                    address=location.address,
                ),
            )
        )

    return response
