from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlmodel import Session, select, and_, func

from app.core.database import get_session
from app.models.event import Event
from app.models.location import Location


router = APIRouter(prefix="/locations", tags=["locations"])

@router.get("/search")
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

@router.get("/map")
async def get_map_locations(
    session: Session = Depends(get_session),
):
    query = (
        select(Location, func.count(Event.id).label("event_count"))
        .outerjoin(Event, Location.id == Event.location_id)
        .where(
            and_(
                Location.latitude != 0.0,
                Location.longitude != 0.0
            )
        )
        .group_by(Location.id)
        .order_by(Location.name.asc())
    )

    results = session.exec(query).all()

    return JSONResponse([
        {
            "id": location.id,
            "name": location.name,
            "subtitle": location.subtitle,
            "address": location.address,
            "latitude": location.latitude,
            "longitude": location.longitude,
            "event_count": event_count,
        }
        for location, event_count in results
    ])