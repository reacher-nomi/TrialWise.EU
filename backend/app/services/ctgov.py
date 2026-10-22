"""Small client for the public ClinicalTrials.gov API v2.

Docs: https://clinicaltrials.gov/data-api/api
No API key is needed. Be polite: don't send hundreds of requests per second.
"""

import httpx

from app.config import get_settings


def _simplify(study: dict) -> dict:
    """Keep only the fields our app needs (the raw JSON is huge)."""
    p = study.get("protocolSection", {})
    ident = p.get("identificationModule", {})
    status = p.get("statusModule", {})
    design = p.get("designModule", {})
    elig = p.get("eligibilityModule", {})
    return {
        "nct_id": ident.get("nctId"),
        "title": ident.get("briefTitle"),
        "status": status.get("overallStatus"),
        "why_stopped": status.get("whyStopped"),
        "enrollment": design.get("enrollmentInfo", {}).get("count"),
        "phases": design.get("phases", []),
        "eligibility_criteria": elig.get("eligibilityCriteria"),
    }


def fetch_studies(condition: str, status: str | None = None, page_size: int = 20) -> dict:
    params: dict[str, str | int] = {"query.cond": condition, "pageSize": page_size}
    if status:
        params["filter.overallStatus"] = status
    url = f"{get_settings().ctgov_base_url}/studies"
    resp = httpx.get(url, params=params, timeout=20)
    resp.raise_for_status()  # turns HTTP errors (4xx/5xx) into exceptions
    data = resp.json()
    return {
        "count": len(data.get("studies", [])),
        "next_page_token": data.get("nextPageToken"),
        "studies": [_simplify(s) for s in data.get("studies", [])],
    }
