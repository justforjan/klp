from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.core.database import create_db_and_tables
from app.core.config import settings
from app.api.events import router as events_router
from app.web import router as web_router
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.core.database import drop_and_create_db
    drop_and_create_db()
    print("Database dropped and recreated")

    from app.services.scraper import run_initial_import
    print("Starting initial data import...")
    try:
        await run_initial_import()
        print("Initial data import completed")
    except Exception as e:
        print(f"Error during import: {e}")
        import traceback
        traceback.print_exc()

    yield

    print("Shutting down...")


app = FastAPI(
    title="Kulturelle Landpartie",
    description="Event listings, locations, and map for KLP",
    version="0.1.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(events_router)
app.include_router(web_router)


@app.get("/")
async def root():
    return {"message": "Welcome to Kulturelle Landpartie"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
