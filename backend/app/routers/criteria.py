from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.db import Analysis, SessionDep
from app.services.extractor import extract_criteria

router = APIRouter(prefix="/criteria", tags=["criteria"])


class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=5, max_length=50_000)
    title: str = "Untitled"
    save: bool = True


@router.post("/analyze")
def analyze(req: AnalyzeRequest, session: SessionDep) -> dict:
    """Feature Set 1 core: eligibility text -> structured criteria with evidence spans."""
    result = extract_criteria(req.text)
    if req.save:
        row = Analysis(title=req.title, source_text=req.text, result=result)
        session.add(row)
        session.commit()
        result["analysis_id"] = row.id
    return result


@router.get("/analyses")
def list_analyses(session: SessionDep) -> list[dict]:
    rows = session.scalars(select(Analysis).order_by(Analysis.id.desc()).limit(50))
    return [
        {"id": r.id, "title": r.title, "created_at": r.created_at, "summary": r.result["summary"]}
        for r in rows
    ]


@router.get("/analyses/{analysis_id}")
def get_analysis(analysis_id: int, session: SessionDep) -> dict:
    row = session.get(Analysis, analysis_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {"id": row.id, "title": row.title, "source_text": row.source_text, **row.result}
