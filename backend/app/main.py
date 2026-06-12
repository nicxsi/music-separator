from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.presentation.routers import separation


def create_app(static_dir: Path | None = None) -> FastAPI:
    app = FastAPI(title="Music Separator")
    app.include_router(separation.router, prefix="/api")   # API routes

    # We give the stems files for playback in the browser
    app.mount(
        "/outputs",
        StaticFiles(directory=str(settings.OUTPUT_DIR)),
        name="outputs",
    )

    # Main HTML statics (catch-all, must be last)
    static_dir = static_dir or (Path(__file__).parent.parent / "static")
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
    return app


app = create_app()
