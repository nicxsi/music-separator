from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.presentation.routers import separation

app = FastAPI(title="Music Separator")

# API routers.
app.include_router(separation.router, prefix="/api")

# Then mount the static files.
static_dir = Path(__file__).parent.parent / "static"
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
