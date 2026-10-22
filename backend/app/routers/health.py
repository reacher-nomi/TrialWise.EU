from fastapi import APIRouter
from sqlalchemy import text

from app.config import get_settings
from app.db import SessionDep

router = APIRouter(tags=["health"])


@router.get("/health")
def health(session: SessionDep) -> dict:
    """The 'one button' check: is the API up, and can it reach the database?"""
    try:
        session.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "unreachable",
        "environment": get_settings().app_env,
    }
