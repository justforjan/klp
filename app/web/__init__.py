from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.core.database import get_session
from app.models.location import Location

from app.web.events import router as events_router
from app.web.locations import router as locations_router
from app.web.favourites import router as favourites_router


router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory="templates")

router.include_router(events_router)
router.include_router(locations_router)
router.include_router(favourites_router)

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/map", response_class=HTMLResponse)
async def map_page(
    request: Request,
    session: Session = Depends(get_session),
):
    query = select(Location).where(
        (Location.latitude == 0.0) | (Location.longitude == 0.0)
    ).order_by(Location.name.asc())
    locations_without_coords = session.exec(query).all()

    return templates.TemplateResponse(
        "map.html",
        {
            "request": request,
            "locations_without_coords": locations_without_coords,
        },
    )