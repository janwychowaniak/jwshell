"""Tests for render output."""

from __future__ import annotations

import io

from rich.console import Console

from jwshell.render import render
from jwshell.schema import AnalysisResult


def _render_to_string(result: AnalysisResult) -> str:
    buf = io.StringIO()
    console = Console(file=buf, force_terminal=False, width=100, color_system=None)
    render(result, console=console)
    return buf.getvalue()


def test_render_command_includes_command_and_explanation() -> None:
    result = AnalysisResult(
        kind="command",
        command="ls -la",
        explanation="Lists all files including hidden ones.",
    )
    out = _render_to_string(result)
    assert "ls -la" in out
    assert "Lists all files" in out
    assert "Notes" not in out
    assert "Suggested command" not in out


def test_render_description_includes_suggested_command_header() -> None:
    result = AnalysisResult(
        kind="description",
        command="find . -name '*.py'",
        explanation="Recursively finds python files.",
    )
    out = _render_to_string(result)
    assert "Suggested command" in out
    assert "find . -name '*.py'" in out
    assert "Recursively finds" in out


def test_render_emits_notes_when_present() -> None:
    result = AnalysisResult(
        kind="command",
        command="rm -rf /tmp/foo",
        explanation="Removes the directory recursively.",
        notes="Destructive: removes without prompting.",
    )
    out = _render_to_string(result)
    assert "Notes" in out
    assert "Destructive" in out
