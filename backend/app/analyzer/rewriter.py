from __future__ import annotations

from typing import Any, cast

from pydantic import BaseModel, Field

from app.analyzer.prompts import REWRITER_SYSTEM_PROMPT
from app.core.config import get_settings
from app.core.llm import LLMClient
from app.models.resume import Bullet, ResumeDoc, Suggestion


class _SuggestionList(BaseModel):
    """Wrapper so the LLM returns one structured object containing many suggestions."""

    suggestions: list[Suggestion] = Field(default_factory=list)


def rewrite_bullets(
    client: LLMClient,
    resume: ResumeDoc,
    role_description: str | None = None,
    bullets: list[Bullet] | None = None,
) -> list[Suggestion]:
    """Generate rewrite suggestions for the given bullets (defaults to all)."""
    settings = get_settings()
    target_bullets = bullets if bullets is not None else resume.all_bullets()
    if not target_bullets:
        return []

    bullets_block = "\n".join(f"- id={b.id} section={b.section}: {b.text}" for b in target_bullets)

    user_blocks: list[dict[str, Any]] = [
        {
            "type": "text",
            "text": f"ResumeDoc context:\n\n{resume.model_dump_json(indent=2)}",
            "cache_control": {"type": "ephemeral"},
        }
    ]
    if role_description:
        user_blocks.append(
            {
                "type": "text",
                "text": f"Target role description:\n\n{role_description}",
            }
        )
    user_blocks.append(
        {
            "type": "text",
            "text": (
                "Bullets to review (one Suggestion per id):\n\n"
                f"{bullets_block}\n\n"
                "Return a SuggestionList containing exactly one Suggestion per bullet id above. "
                "Use the bullet id verbatim as Suggestion.bullet_id."
            ),
        }
    )

    response = cast(Any, client).messages.parse(
        model=settings.anthropic_model,
        max_tokens=8000,
        system=[
            {
                "type": "text",
                "text": REWRITER_SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_blocks}],
        output_format=_SuggestionList,
    )
    parsed = cast(_SuggestionList | None, response.parsed_output)
    if parsed is None:
        return []
    valid_ids = {b.id for b in target_bullets}
    return [s for s in parsed.suggestions if s.bullet_id in valid_ids]
