from __future__ import annotations

from typing import Any, cast

from app.analyzer.prompts import GAP_FINDER_SYSTEM_PROMPT
from app.core.config import get_settings
from app.core.llm import LLMClient
from app.models.resume import GapReport, ResumeDoc


def find_gaps(client: LLMClient, resume: ResumeDoc) -> GapReport:
    settings = get_settings()
    response = cast(Any, client).messages.parse(
        model=settings.anthropic_model,
        max_tokens=4000,
        system=[
            {
                "type": "text",
                "text": GAP_FINDER_SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"ResumeDoc to review:\n\n{resume.model_dump_json(indent=2)}",
                        "cache_control": {"type": "ephemeral"},
                    },
                    {
                        "type": "text",
                        "text": "Return a GapReport with document-level findings. Leave suggestions and keyword_overlap empty.",
                    },
                ],
            }
        ],
        output_format=GapReport,
    )
    parsed = cast(GapReport | None, response.parsed_output)
    if parsed is None:
        return GapReport(ats_score=50)
    parsed.suggestions = []
    parsed.keyword_overlap = {}
    return parsed
