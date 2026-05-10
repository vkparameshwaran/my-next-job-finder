"""Anthropic client provider — dependency-injectable so tests can swap a fake."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import anthropic
from fastapi import Depends

from app.core.config import Settings, get_settings


@runtime_checkable
class LLMClient(Protocol):
    """Minimal Protocol covering the Anthropic methods we call.

    Tests provide a fake implementing this Protocol; production code receives
    a real `anthropic.Anthropic` instance. The Protocol exists only as a
    typing hint — the real client and the fake share no base class.
    """

    @property
    def messages(self) -> object: ...

    @property
    def beta(self) -> object: ...


_real_client: anthropic.Anthropic | None = None
_fake_client: LLMClient | None = None


def get_llm_client(settings: Settings = Depends(get_settings)) -> LLMClient:
    global _real_client, _fake_client
    if settings.use_fake_llm:
        if _fake_client is None:
            from app.core.dev_fake import DevFakeAnthropic

            _fake_client = DevFakeAnthropic()
        return _fake_client
    if _real_client is None:
        _real_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    return _real_client


def reset_llm_client() -> None:
    """Test helper — clears the cached client."""
    global _real_client, _fake_client
    _real_client = None
    _fake_client = None
