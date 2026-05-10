"""Turn raw resume text into a structured ResumeDoc using Claude.

Uses messages.parse() with the ResumeDoc Pydantic model so the LLM is
schema-bound — no regex parsing of the response. Prompt caching is enabled
on the resume content since the same raw text is reused by the analyzer
within the same session.
"""

from __future__ import annotations

from typing import Any, cast

from app.core.config import get_settings
from app.core.llm import LLMClient
from app.models.resume import ResumeDoc

STRUCTURE_SYSTEM_PROMPT = """You are an expert resume parser for the Indian tech job market.

Your job: read the raw text of a resume and return a structured ResumeDoc.

Guidelines:
- Preserve bullet text verbatim. Do not paraphrase, summarize, or "clean up" wording.
- If a section is missing, return an empty list — do not invent content.
- For dates, return the strings as written (e.g. "Jun 2021", "Present", "2019-2022").
- Skills: extract the items the candidate explicitly lists. Do not infer skills from bullets.
- Always set raw_text to the full input text exactly as received."""


def structure_resume(client: LLMClient, raw_text: str) -> ResumeDoc:
    settings = get_settings()
    response = cast(Any, client).messages.parse(
        model=settings.anthropic_model,
        max_tokens=8000,
        system=[
            {
                "type": "text",
                "text": STRUCTURE_SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Raw resume text:\n\n{raw_text}",
                        "cache_control": {"type": "ephemeral"},
                    },
                    {
                        "type": "text",
                        "text": "Return a ResumeDoc that exactly represents this resume.",
                    },
                ],
            }
        ],
        output_format=ResumeDoc,
    )
    parsed = response.parsed_output
    if parsed is None:
        raise ValueError("LLM did not return a parseable ResumeDoc")
    parsed.raw_text = raw_text
    return parsed
