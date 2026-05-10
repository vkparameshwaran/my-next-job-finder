"""Deterministic fake Anthropic client for local smoke-testing without
hitting the API. Activated by setting USE_FAKE_LLM=true in .env.

The fake produces plausible-but-canned ResumeDoc / GapReport / suggestion
list responses derived from the raw resume text. Good enough to verify the
full pipeline (upload → parse → analyze → export) works end-to-end.

Do NOT use this in production — that's what `app.core.llm.get_llm_client`
is for. This module is import-gated behind the env flag.
"""

from __future__ import annotations

import re
from types import SimpleNamespace
from typing import Any

_LABEL_PREFIXES = (
    "Raw resume text:",
    "ResumeDoc context:",
    "ResumeDoc to review:",
    "Target role description:",
    "Bullets to review",
)


def _strip_label(text: str) -> str:
    """Strip the leading 'Raw resume text:' / 'ResumeDoc context:' label our
    analyzer code prepends, so the heuristic parser sees the real content."""
    for prefix in _LABEL_PREFIXES:
        if text.startswith(prefix):
            return text[len(prefix) :].lstrip()
    return text


def _extract_user_text(messages: list[dict[str, Any]]) -> str:
    """Pull the resume / context text out of the request message blocks."""
    for msg in messages:
        if msg.get("role") != "user":
            continue
        content = msg.get("content", [])
        if isinstance(content, str):
            return _strip_label(content)
        if isinstance(content, list):
            for block in content:
                if not isinstance(block, dict):
                    continue
                text = block.get("text", "")
                if not text:
                    continue
                stripped = _strip_label(text)
                if stripped.startswith("{"):
                    continue
                return stripped
    return ""


def _heuristic_resume_doc(raw_text: str) -> Any:
    from app.models.resume import (
        Bullet,
        Contact,
        Job,
        ResumeDoc,
    )

    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    name = lines[0] if lines else "Candidate Name"

    email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", raw_text)
    phone_match = re.search(r"\+?\d[\d\s\-()]{8,}\d", raw_text)
    contact = Contact(
        name=name,
        email=email_match.group(0) if email_match else None,
        phone=phone_match.group(0) if phone_match else None,
    )

    bullet_lines = [
        line for line in lines[1:] if len(line.split()) >= 4 and not line.endswith(":")
    ][:5]
    bullets = [
        Bullet(text=line, section="experience", parent_id="job-fake")
        for line in bullet_lines
    ]

    job = Job(
        id="job-fake",
        company="Sample Company",
        title="Software Engineer",
        start_date="Jan 2022",
        end_date="Present",
        bullets=bullets,
    )
    return ResumeDoc(
        contact=contact,
        summary=None,
        experience=[job] if bullets else [],
        skills=["Python", "JavaScript", "Docker"],
        raw_text=raw_text,
    )


def _canned_gap_report() -> Any:
    from app.models.resume import GapReport, Issue

    return GapReport(
        ats_score=68,
        issues=[
            Issue(
                kind="missing_summary",
                message="Resume has no professional summary section.",
                severity="warning",
            ),
            Issue(
                kind="no_metric",
                message="Multiple bullets lack quantified outcomes.",
                severity="warning",
            ),
        ],
        suggestions=[],
        keyword_overlap={},
    )


def _canned_suggestions(resume_doc: Any) -> Any:
    from app.analyzer.rewriter import _SuggestionList
    from app.models.resume import Suggestion

    suggestions = [
        Suggestion(
            bullet_id=bullet.id,
            issue="weak_verb",
            rationale="Replaced passive phrasing with a strong action verb.",
            rewrite=f"Shipped {bullet.text.lower()[:60]} [QUANTIFY].",
        )
        for bullet in resume_doc.all_bullets()
    ]
    return _SuggestionList(suggestions=suggestions)


class _FakeMessages:
    def __init__(self) -> None:
        self._last_resume: Any = None

    def parse(
        self,
        *,
        output_format: type,
        messages: list[dict[str, Any]] | None = None,
        **_kwargs: Any,
    ) -> SimpleNamespace:
        from app.analyzer.rewriter import _SuggestionList
        from app.models.resume import GapReport, ResumeDoc

        user_text = _extract_user_text(messages or [])

        if output_format is ResumeDoc:
            self._last_resume = _heuristic_resume_doc(user_text)
            return SimpleNamespace(parsed_output=self._last_resume)
        if output_format is GapReport:
            return SimpleNamespace(parsed_output=_canned_gap_report())
        if output_format is _SuggestionList:
            resume = self._last_resume or _heuristic_resume_doc(user_text)
            return SimpleNamespace(parsed_output=_canned_suggestions(resume))

        raise NotImplementedError(
            f"DevFakeAnthropic does not support output_format={output_format!r}"
        )


class DevFakeAnthropic:
    """Deterministic stand-in for `anthropic.Anthropic` for local dev / smoke tests."""

    def __init__(self) -> None:
        self.messages = _FakeMessages()
        self.beta = SimpleNamespace(messages=self.messages)
