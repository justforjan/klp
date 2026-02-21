from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from app.core.database import get_session

router = APIRouter(prefix="/favourites", tags=["locations"])
templates = Jinja2Templates(directory="templates")

@router.get("", response_class=HTMLResponse)
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
