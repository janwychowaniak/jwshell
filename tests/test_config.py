"""Tests for configuration loading."""

from __future__ import annotations

import pytest

from jwshell.config import API_KEY_ENV, DEFAULT_MODEL, MODEL_ENV, ConfigError, load_config


def test_load_config_uses_env_key_and_default_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(API_KEY_ENV, "abc")
    monkeypatch.delenv(MODEL_ENV, raising=False)
    cfg = load_config()
    assert cfg.api_key == "abc"
    assert cfg.model == DEFAULT_MODEL


def test_model_env_overrides_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(API_KEY_ENV, "abc")
    monkeypatch.setenv(MODEL_ENV, "openai/gpt-5.2")
    cfg = load_config()
    assert cfg.model == "openai/gpt-5.2"


def test_explicit_override_beats_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(API_KEY_ENV, "abc")
    monkeypatch.setenv(MODEL_ENV, "openai/gpt-5.2")
    cfg = load_config(model_override="anthropic/claude-sonnet-4.6")
    assert cfg.model == "anthropic/claude-sonnet-4.6"


def test_missing_key_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(API_KEY_ENV, raising=False)
    with pytest.raises(ConfigError, match=API_KEY_ENV):
        load_config()


def test_blank_key_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(API_KEY_ENV, "   ")
    with pytest.raises(ConfigError):
        load_config()
