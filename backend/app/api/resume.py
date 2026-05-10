from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlmodel import Session

from app.analyzer.pipeline import analyze
from app.core.db import get_session
from app.core.llm import LLMClient, get_llm_client
from app.exporter.docx_writer import build_docx
from app.models.resume import (
    AnalyzeResponse,
    GapReport,
    ResumeDoc,
    ResumeRecord,
    Suggestion,
)
from app.parsers.docx_parser import extract_text_from_docx
from app.parsers.pdf_parser import extract_text_from_pdf
from app.parsers.structurer import structure_resume

router = APIRouter()

_PDF_TYPES = {"application/pdf"}
_DOCX_TYPES = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
_MAX_BYTES = 5 * 1024 * 1024


@router.post("/upload", response_model=AnalyzeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    role_description: str | None = Form(default=None),
    session: Session = Depends(get_session),
    llm: LLMClient = Depends(get_llm_client),
) -> AnalyzeResponse:
    data = await file.read()
    if len(data) > _MAX_BYTES:
        raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, "File too large (max 5MB)")
    if file.content_type in _PDF_TYPES or (file.filename or "").lower().endswith(".pdf"):
        raw_text = extract_text_from_pdf(data)
    elif file.content_type in _DOCX_TYPES or (file.filename or "").lower().endswith(".docx"):
        raw_text = extract_text_from_docx(data)
    else:
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Unsupported file type: {file.content_type}",
        )
    if not raw_text.strip():
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Could not extract text from file"
        )

    resume = structure_resume(llm, raw_text)
    report = analyze(llm, resume, role_description=role_description)

    record = ResumeRecord(
        filename=file.filename or "resume",
        resume_json=resume.model_dump(),
        report_json=report.model_dump(),
        role_description=role_description,
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return AnalyzeResponse(record_id=record.id, resume=resume, report=report)


@router.get("/{record_id}", response_model=AnalyzeResponse)
def get_resume(record_id: str, session: Session = Depends(get_session)) -> AnalyzeResponse:
    record = session.get(ResumeRecord, record_id)
    if record is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resume not found")
    return AnalyzeResponse(
        record_id=record.id,
        resume=ResumeDoc.model_validate(record.resume_json),
        report=GapReport.model_validate(record.report_json or {"ats_score": 0}),
    )


@router.post("/{record_id}/export")
def export_resume(
    record_id: str,
    accepted: list[Suggestion],
    session: Session = Depends(get_session),
) -> Response:
    record = session.get(ResumeRecord, record_id)
    if record is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resume not found")
    resume = ResumeDoc.model_validate(record.resume_json)
    docx_bytes = build_docx(resume, accepted_suggestions=accepted)
    return Response(
        content=docx_bytes,
        media_type=("application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
        headers={
            "Content-Disposition": f'attachment; filename="{record.filename}-tweaked.docx"',
        },
    )
