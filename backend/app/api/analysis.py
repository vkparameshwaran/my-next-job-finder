from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.analyzer.pipeline import analyze
from app.core.db import get_session
from app.core.llm import LLMClient, get_llm_client
from app.models.resume import AnalyzeRequest, AnalyzeResponse, ResumeDoc, ResumeRecord

router = APIRouter()


@router.post("/{record_id}", response_model=AnalyzeResponse)
def reanalyze(
    record_id: str,
    request: AnalyzeRequest,
    session: Session = Depends(get_session),
    llm: LLMClient = Depends(get_llm_client),
) -> AnalyzeResponse:
    record = session.get(ResumeRecord, record_id)
    if record is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resume not found")
    resume = ResumeDoc.model_validate(record.resume_json)
    report = analyze(llm, resume, role_description=request.role_description)

    record.report_json = report.model_dump()
    record.role_description = request.role_description
    session.add(record)
    session.commit()
    return AnalyzeResponse(record_id=record.id, resume=resume, report=report)
