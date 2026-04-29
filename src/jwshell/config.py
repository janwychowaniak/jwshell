"""Runtime configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass

API_KEY_ENV = "JWSHELL_OR_APIKEY"
MODEL_ENV = "JWSHELL_OR_MODEL"
DEFAULT_MODEL = "anthropic/claude-haiku-4.5"


class ConfigError(Exception):
    """Raised when required configuration is missing or invalid."""


@dataclass(frozen=True, slots=True)
class Config:
    api_key: str
    model: str


def load_config(*, model_override: str | None = None) -> Config:
    api_key = os.environ.get(API_KEY_ENV, "").strip()
    if not api_key:
        raise ConfigError(
            f"{API_KEY_ENV} is not set. Get a key at https://openrouter.ai/keys "
            f"and export it before running jwshell.",
        )
    model = (model_override or os.environ.get(MODEL_ENV) or DEFAULT_MODEL).strip()
    if not model:
        raise ConfigError(f"{MODEL_ENV} is set to an empty value.")
    return Config(api_key=api_key, model=model)
