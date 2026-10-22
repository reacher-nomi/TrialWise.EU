import httpx
from fastapi import APIRouter, HTTPException, Query

from app.services.ctgov import fetch_studies

router = APIRouter(prefix="/trials", tags=["trials"])


@router.get("/search")
def search_trials(
    condition: str = Query(min_length=2, examples=["non-small cell lung cancer"]),
    status: str | None = Query(default=None, examples=["TERMINATED"]),
    page_size: int = Query(default=20, ge=1, le=100),
) -> dict:
    """Search ClinicalTrials.gov. Tip: status=TERMINATED + look at why_stopped
    to find trials that failed because of low recruitment (Feature Set 2 idea)."""
    try:
        return fetch_studies(condition, status, page_size)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"ClinicalTrials.gov error: {exc}") from exc
