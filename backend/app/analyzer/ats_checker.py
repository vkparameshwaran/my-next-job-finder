"""Deterministic ATS checks. Runs locally — no LLM. Computes keyword overlap
between the resume and (optional) job description."""

from __future__ import annotations

import re

from app.models.resume import ResumeDoc

_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9+#\.\-]{1,}")
_STOP_WORDS = frozenset(
    {
        "and",
        "or",
        "the",
        "a",
        "an",
        "to",
        "of",
        "in",
        "for",
        "on",
        "at",
        "by",
        "with",
        "from",
        "as",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "this",
        "that",
        "these",
        "those",
        "it",
        "its",
        "we",
        "you",
        "your",
        "our",
        "they",
        "them",
        "their",
        "will",
        "would",
        "should",
        "can",
        "could",
        "may",
        "might",
        "must",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "but",
        "if",
        "then",
        "else",
        "than",
        "such",
        "no",
        "not",
        "only",
        "own",
        "same",
        "so",
        "very",
        "s",
        "t",
        "just",
        "about",
        "also",
        "more",
        "most",
        "other",
    }
)


def _tokenize(text: str) -> set[str]:
    tokens = (m.group(0).lower() for m in _TOKEN_RE.finditer(text))
    return {t for t in tokens if t not in _STOP_WORDS and len(t) > 2}


def keyword_overlap(resume: ResumeDoc, job_description: str | None) -> dict[str, bool]:
    """For each meaningful token in the JD, mark whether it appears in the resume."""
    if not job_description:
        return {}
    jd_tokens = _tokenize(job_description)
    resume_tokens = _tokenize(resume.raw_text)
    return {token: token in resume_tokens for token in sorted(jd_tokens)}


def overlap_ratio(overlap: dict[str, bool]) -> float:
    if not overlap:
        return 0.0
    hits = sum(1 for v in overlap.values() if v)
    return hits / len(overlap)
