"""Structured-output schema for the LLM response."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

ResultKind = Literal["command", "description"]


class AnalysisResult(BaseModel):
    """Typed result returned by the LLM for a single jwshell invocation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    kind: ResultKind = Field(
        description=(
            "'command' when the user input is a valid bash/zsh command or expression; "
            "'description' when the input is a natural-language description of a desired effect."
        ),
    )
    command: str = Field(
        description=(
            "The shell command. When kind=='command', this is the (optionally normalised) "
            "input. When kind=='description', this is the generated command that achieves "
            "the described effect."
        ),
    )
    explanation: str = Field(
        description=(
            "Plain-text explanation. When kind=='command', explain what the command does "
            "(brief or detailed depending on the verbosity hint). When kind=='description', "
            "explain why the generated command matches the request."
        ),
    )
    notes: str = Field(
        default="",
        description=(
            "Optional caveats: destructive flags, shell-dialect differences, assumptions made, "
            "or alternative variants. Use an empty string when there is nothing to add."
        ),
    )


def _strict_schema(model: type[BaseModel], name: str) -> dict[str, Any]:
    """Return a strict JSON schema suitable for OpenRouter's structured outputs.

    Pydantic does not emit ``additionalProperties: false`` by default, and strict mode
    requires every declared property to appear in ``required``.
    """
    schema = model.model_json_schema()
    schema.pop("title", None)
    schema["additionalProperties"] = False
    properties = schema.get("properties", {})
    schema["required"] = list(properties.keys())
    schema["$schema"] = "http://json-schema.org/draft-07/schema#"
    schema["name"] = name
    return schema


def response_format() -> dict[str, Any]:
    """Build the ``response_format`` payload for OpenRouter's chat.send."""
    schema = _strict_schema(AnalysisResult, "AnalysisResult")
    schema_only = {k: v for k, v in schema.items() if k != "name"}
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "AnalysisResult",
            "strict": True,
            "schema_": schema_only,
        },
    }
