"""Source-of-truth Pydantic schemas. The entire pipeline (parser → analyzer →
exporter → frontend) speaks these types."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field
from sqlmodel import JSON, Column, SQLModel
from sqlmodel import Field as SQLField


def _new_id() -> str:
    return uuid4().hex[:12]


SectionKind = Literal["experience", "projects", "education"]
IssueKind = Literal[
    "no_metric",
    "weak_verb",
    "vague",
    "passive_voice",
    "keyword_miss",
    "redundant",
    "too_long",
    "ats_unfriendly",
    "missing_summary",
    "timeline_gap",
    "short_stint",
]


class Contact(BaseModel):
    name: str = ""
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    linkedin: str | None = None
    github: str | None = None
    portfolio: str | None = None


class Bullet(BaseModel):
    id: str = Field(default_factory=_new_id)
    text: str
    section: SectionKind
    parent_id: str


class Job(BaseModel):
    id: str = Field(default_factory=_new_id)
    company: str
    title: str
    location: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    bullets: list[Bullet] = Field(default_factory=list)


class Project(BaseModel):
    id: str = Field(default_factory=_new_id)
    name: str
    link: str | None = None
    description: str | None = None
    bullets: list[Bullet] = Field(default_factory=list)


class Degree(BaseModel):
    id: str = Field(default_factory=_new_id)
    institution: str
    qualification: str
    field_of_study: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    grade: str | None = None
    bullets: list[Bullet] = Field(default_factory=list)


class ResumeDoc(BaseModel):
    contact: Contact = Field(default_factory=Contact)
    summary: str | None = None
    experience: list[Job] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    education: list[Degree] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    raw_text: str = ""

    def all_bullets(self) -> list[Bullet]:
        bullets: list[Bullet] = []
        for job in self.experience:
            bullets.extend(job.bullets)
        for project in self.projects:
            bullets.extend(project.bullets)
        for degree in self.education:
            bullets.extend(degree.bullets)
        return bullets


class Issue(BaseModel):
    """A high-level, document-wide finding."""

    kind: IssueKind
    message: str
    severity: Literal["info", "warning", "error"] = "warning"


class Suggestion(BaseModel):
    """A bullet-level rewrite proposal."""

    id: str = Field(default_factory=_new_id)
    bullet_id: str
    issue: IssueKind
    rationale: str
    rewrite: str
    accepted: bool | None = None


class GapReport(BaseModel):
    ats_score: int = Field(ge=0, le=100)
    issues: list[Issue] = Field(default_factory=list)
    suggestions: list[Suggestion] = Field(default_factory=list)
    keyword_overlap: dict[str, bool] = Field(default_factory=dict)


class AnalyzeRequest(BaseModel):
    role_description: str | None = None


class AnalyzeResponse(BaseModel):
    record_id: str
    resume: ResumeDoc
    report: GapReport


class ResumeRecord(SQLModel, table=True):
    """Persisted record of a parsed resume + its analysis."""

    id: str = SQLField(default_factory=_new_id, primary_key=True)
    created_at: datetime = SQLField(default_factory=lambda: datetime.now(UTC))
    filename: str
    resume_json: dict = SQLField(default_factory=dict, sa_column=Column(JSON))
    report_json: dict | None = SQLField(default=None, sa_column=Column(JSON))
    role_description: str | None = None
    accepted_suggestion_ids: list[str] = SQLField(default_factory=list, sa_column=Column(JSON))
