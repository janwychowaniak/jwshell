"""Thin OpenRouter client wrapper that performs the single classify+answer call."""

from __future__ import annotations

from typing import TYPE_CHECKING

from openrouter import OpenRouter
from pydantic import ValidationError

from jwshell.prompts import system_prompt
from jwshell.schema import AnalysisResult, response_format

if TYPE_CHECKING:
    from jwshell.config import Config


class JwshellError(Exception):
    """Top-level error raised for any failure of the jwshell pipeline."""


def analyze(text: str, *, verbose: bool, cfg: Config) -> AnalysisResult:
    """Send a single chat request and return the parsed structured result.

    Raises ``JwshellError`` for empty model output or schema-validation failures so the CLI
    can surface a friendly message. OpenRouter SDK errors propagate unchanged for the
    caller to format.
    """
    messages = [
        {"role": "system", "content": system_prompt(verbose=verbose)},
        {"role": "user", "content": text},
    ]
    with OpenRouter(api_key=cfg.api_key) as client:
        result = client.chat.send(
            model=cfg.model,
            messages=messages,
            response_format=response_format(),
        )

    if not result.choices:
        raise JwshellError("OpenRouter returned no choices.")
    content = result.choices[0].message.content
    if not isinstance(content, str) or not content.strip():
        raise JwshellError("OpenRouter returned an empty or non-text response.")

    try:
        return AnalysisResult.model_validate_json(content)
    except ValidationError as exc:
        raise JwshellError(f"Model output did not match expected schema: {exc}") from exc
