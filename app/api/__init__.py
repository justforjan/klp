from fastapi import APIRouter

from app.api.events import router as events_router
from app.api.favourites import router as favourites_router
from app.api.locations import router as locations_router

router = APIRouter(prefix="/api", tags=["api"])

router.include_router(events_router)
router.include_router(favourites_router)
router.include_router(locations_router)


