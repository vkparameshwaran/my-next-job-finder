"""Test fixtures. The fake Anthropic client lives here so every test can
override `get_llm_client` without touching the network or burning API
credits in CI.
"""

from __future__ import annotations

import os
import tempfile
from collections.abc import Iterator
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

os.environ.setdefault("ANTHROPIC_API_KEY", "sk-test-not-a-real-key")
os.environ.setdefault("ANTHROPIC_MODEL", "claude-sonnet-4-6")


class FakeMessages:
    """Stand-in for client.messages — only `parse` is implemented."""

    def __init__(self, responses: dict[type, Any]) -> None:
        self._responses = responses

    def parse(self, *, output_format: type, **_kwargs: Any) -> SimpleNamespace:
        if output_format not in self._responses:
            raise AssertionError(
                f"FakeMessages.parse received unexpected output_format={output_format}"
            )
        instance = self._responses[output_format]
        return SimpleNamespace(parsed_output=instance)


class FakeAnthropic:
    """Drop-in replacement for `anthropic.Anthropic` for tests."""

    def __init__(self, responses: dict[type, Any] | None = None) -> None:
        self._responses: dict[type, Any] = responses or {}
        self.messages = FakeMessages(self._responses)
        self.beta = SimpleNamespace(messages=FakeMessages(self._responses))

    def queue(self, response: Any) -> None:
        self._responses[type(response)] = response


@pytest.fixture
def fake_anthropic() -> FakeAnthropic:
    return FakeAnthropic()


@pytest.fixture
def temp_db(monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
        from app.core.config import get_settings

        get_settings.cache_clear()
        yield db_path


@pytest.fixture
def client(temp_db: Path, fake_anthropic: FakeAnthropic) -> Iterator[TestClient]:
    from app.core.db import get_session
    from app.core.llm import get_llm_client, reset_llm_client
    from app.main import create_app

    engine = create_engine(
        f"sqlite:///{temp_db}",
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(engine)

    app = create_app()

    def _override_session() -> Iterator[Session]:
        with Session(engine) as s:
            yield s

    app.dependency_overrides[get_session] = _override_session
    app.dependency_overrides[get_llm_client] = lambda: fake_anthropic

    reset_llm_client()
    yield TestClient(app)
    app.dependency_overrides.clear()
    reset_llm_client()
