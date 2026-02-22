from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
import time
import asyncio
import uvicorn

from app.config import settings
from app.api import router as api_router
from app.web import router as web_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.core.database import run_migrations

    run_migrations(reset=settings.reload_data)

    try:
        if settings.reload_data:
            from app.services.scraper import run_initial_import
            print("Starting data import...")
            await run_initial_import()

        if settings.run_geocode:
            from app.services.geocoding import geocode_locations
            print("Starting geocoding...")
            asyncio.create_task(geocode_locations())

        if settings.get_embeddings:
            from app.services.embedding import add_embeddings
            print("Starting embeddings...")
            add_embeddings()
            print("Embeddings completed")

    except Exception as e:
        print(f"Error during startup: {e}")
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



@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    # ANSI color codes
    colors = {
        "GET": "\033[1;32m",  # Bold Green
        "POST": "\033[1;34m",  # Bold Blue
        "PUT": "\033[1;33m",  # Bold Yellow
        "PATCH": "\033[1;35m",  # Bold Magenta
        "DELETE": "\033[1;31m",  # Bold Red
        "HEAD": "\033[1;36m",  # Bold Cyan
        "OPTIONS": "\033[1;37m",  # Bold White
    }
    reset = "\033[0m"

    color = colors.get(request.method, "\033[1m")  # Default to just bold

    url = str(request.url.path)
    if request.url.query:
        url += f"?{request.url.query}"

    print(f"{color}{request.method}{reset} {url} - {response.status_code} - {process_time:.3f}s")

    return response


app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(api_router)
app.include_router(web_router)


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info",
        access_log=True,
    )
