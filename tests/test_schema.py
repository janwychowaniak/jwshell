"""Tests for schema construction and JSON serialization."""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from jwshell.schema import AnalysisResult, response_format


def test_default_notes_is_empty_string() -> None:
    result = AnalysisResult(kind="command", command="ls", explanation="lists files")
    assert result.notes == ""


def test_command_round_trip() -> None:
    payload = {
        "kind": "command",
        "command": "ls -la",
        "explanation": "Lists all files including hidden ones in long format.",
        "notes": "",
    }
    parsed = AnalysisResult.model_validate_json(json.dumps(payload))
    assert parsed.kind == "command"
    assert parsed.command == "ls -la"
    assert parsed.notes == ""


def test_description_round_trip() -> None:
    payload = {
        "kind": "description",
        "command": "find . -name '*.py' -mtime -1",
        "explanation": "Finds python files modified within the last day.",
        "notes": "Use -mtime 0 to limit to today only.",
    }
    parsed = AnalysisResult.model_validate_json(json.dumps(payload))
    assert parsed.kind == "description"
    assert "find" in parsed.command
    assert parsed.notes.startswith("Use -mtime")


def test_invalid_kind_rejected() -> None:
    with pytest.raises(ValidationError):
        AnalysisResult(kind="other", command="x", explanation="y")  # type: ignore[arg-type]


def test_extra_fields_rejected() -> None:
    with pytest.raises(ValidationError):
        AnalysisResult.model_validate(
            {
                "kind": "command",
                "command": "ls",
                "explanation": "lists",
                "extra": "nope",
            },
        )


def test_response_format_is_strict_json_schema() -> None:
    rf = response_format()
    assert rf["type"] == "json_schema"
    js = rf["json_schema"]
    assert js["name"] == "AnalysisResult"
    assert js["strict"] is True
    schema = js["schema_"]
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == {"kind", "command", "explanation", "notes"}
    assert schema["properties"]["kind"]["enum"] == ["command", "description"]
