"""Compose the analyzer passes into a single GapReport."""

from __future__ import annotations

from app.analyzer.ats_checker import keyword_overlap, overlap_ratio
from app.analyzer.gap_finder import find_gaps
from app.analyzer.rewriter import rewrite_bullets
from app.core.llm import LLMClient
from app.models.resume import GapReport, ResumeDoc


def analyze(
    client: LLMClient,
    resume: ResumeDoc,
    role_description: str | None = None,
) -> GapReport:
    report = find_gaps(client, resume)
    suggestions = rewrite_bullets(client, resume, role_description=role_description)
    overlap = keyword_overlap(resume, role_description)

    final_score = report.ats_score
    if overlap:
        keyword_component = int(overlap_ratio(overlap) * 100)
        final_score = (report.ats_score + keyword_component) // 2

    return GapReport(
        ats_score=final_score,
        issues=report.issues,
        suggestions=suggestions,
        keyword_overlap=overlap,
    )
