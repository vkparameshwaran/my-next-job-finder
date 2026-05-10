from __future__ import annotations

from app.analyzer.gap_finder import find_gaps
from app.analyzer.pipeline import analyze
from app.analyzer.rewriter import _SuggestionList, rewrite_bullets
from app.models.resume import (
    Bullet,
    GapReport,
    Issue,
    Job,
    ResumeDoc,
    Suggestion,
)
from tests.conftest import FakeAnthropic


def _sample_resume() -> ResumeDoc:
    bullet = Bullet(
        id="b1",
        text="Was responsible for various backend things",
        section="experience",
        parent_id="job-1",
    )
    return ResumeDoc(
        experience=[
            Job(id="job-1", company="Acme", title="SWE", bullets=[bullet]),
        ],
        skills=["python"],
        raw_text="Skills: Python\nWas responsible for various backend things",
    )


def test_find_gaps_returns_report_and_strips_suggestions(fake_anthropic: FakeAnthropic) -> None:
    fake_report = GapReport(
        ats_score=72,
        issues=[Issue(kind="vague", message="bullets are vague")],
        suggestions=[Suggestion(bullet_id="b1", issue="vague", rationale="x", rewrite="y")],
        keyword_overlap={"react": True},
    )
    fake_anthropic.queue(fake_report)

    report = find_gaps(fake_anthropic, _sample_resume())

    assert report.ats_score == 72
    assert report.issues[0].kind == "vague"
    assert report.suggestions == []
    assert report.keyword_overlap == {}


def test_rewrite_bullets_filters_invalid_ids(fake_anthropic: FakeAnthropic) -> None:
    suggestions = _SuggestionList(
        suggestions=[
            Suggestion(bullet_id="b1", issue="weak_verb", rationale="lead", rewrite="Built X"),
            Suggestion(bullet_id="ghost", issue="vague", rationale="-", rewrite="Z"),
        ]
    )
    fake_anthropic.queue(suggestions)

    out = rewrite_bullets(fake_anthropic, _sample_resume())

    assert len(out) == 1
    assert out[0].bullet_id == "b1"


def test_pipeline_combines_score_with_keyword_overlap(fake_anthropic: FakeAnthropic) -> None:
    fake_anthropic.queue(GapReport(ats_score=80, issues=[]))
    fake_anthropic.queue(_SuggestionList(suggestions=[]))

    report = analyze(
        fake_anthropic,
        _sample_resume(),
        role_description="React engineer with Python experience",
    )

    assert report.keyword_overlap["python"] is True
    assert report.keyword_overlap["react"] is False
    assert 0 <= report.ats_score <= 100


def test_rewrite_bullets_returns_empty_when_no_targets(fake_anthropic: FakeAnthropic) -> None:
    empty_resume = ResumeDoc(raw_text="")
    out = rewrite_bullets(fake_anthropic, empty_resume)
    assert out == []


def test_pipeline_handles_no_jd(fake_anthropic: FakeAnthropic) -> None:
    fake_anthropic.queue(GapReport(ats_score=60, issues=[]))
    fake_anthropic.queue(_SuggestionList(suggestions=[]))
    report = analyze(fake_anthropic, _sample_resume(), role_description=None)
    assert report.keyword_overlap == {}
    assert report.ats_score == 60
