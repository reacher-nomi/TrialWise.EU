"""FastAPI entry point. Run locally with:  uv run fastapi dev app/main.py

Interactive API docs appear at http://localhost:8000/docs
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import init_db
from app.routers import criteria, health, trials


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # runs once at startup: create tables if missing
    yield


app = FastAPI(title="TrialWise API", version="0.1.0", lifespan=lifespan)

# Every route lives under /api so the frontend can proxy one path.
for r in (health.router, criteria.router, trials.router):
    app.include_router(r, prefix="/api")
