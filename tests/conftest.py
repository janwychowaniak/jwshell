"""Shared pytest fixtures."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Iterator

from jwshell.config import API_KEY_ENV, MODEL_ENV


@pytest.fixture
def with_env(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Provide a valid API key environment for tests that need configuration to load."""
    monkeypatch.setenv(API_KEY_ENV, "test-key-do-not-use")
    monkeypatch.delenv(MODEL_ENV, raising=False)
    yield


@pytest.fixture
def no_env(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Ensure environment is fully unset for tests that exercise the missing-key path."""
    monkeypatch.delenv(API_KEY_ENV, raising=False)
    monkeypatch.delenv(MODEL_ENV, raising=False)
    yield
