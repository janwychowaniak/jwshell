"""End-to-end CLI tests using Typer's CliRunner with the LLM call mocked."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from jwshell import __version__
from jwshell.cli import app
from jwshell.schema import AnalysisResult

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

runner = CliRunner()


def test_version_flag_prints_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_no_args_shows_help() -> None:
    result = runner.invoke(app, [])
    # no_args_is_help renders the help text and exits with code 0 or 2 depending on version
    assert "INPUT" in result.stdout or "INPUT" in result.stderr


def test_missing_api_key_errors_out(no_env: None) -> None:
    result = runner.invoke(app, ["ls -la"])
    assert result.exit_code == 1
    assert "JWSHELL_OR_APIKEY" in result.stderr


def test_command_path_renders_explanation(with_env: None, mocker: MockerFixture) -> None:
    fake = AnalysisResult(
        kind="command",
        command="ls -la",
        explanation="Lists all files including hidden in long format.",
    )
    mocker.patch("jwshell.cli.analyze", return_value=fake)
    result = runner.invoke(app, ["ls -la"])
    assert result.exit_code == 0, result.stderr
    assert "ls -la" in result.stdout
    assert "Lists all files" in result.stdout


def test_description_path_renders_suggested_command(with_env: None, mocker: MockerFixture) -> None:
    fake = AnalysisResult(
        kind="description",
        command="find . -name '*.py' -mtime -1",
        explanation="Recursively finds Python files modified in the last day.",
        notes="Use -mtime 0 for today only.",
    )
    mocker.patch("jwshell.cli.analyze", return_value=fake)
    result = runner.invoke(app, ["find python files modified today"])
    assert result.exit_code == 0, result.stderr
    assert "Suggested command" in result.stdout
    assert "find . -name" in result.stdout
    assert "Notes" in result.stdout
    assert "today only" in result.stdout


def test_verbose_flag_is_forwarded(with_env: None, mocker: MockerFixture) -> None:
    fake = AnalysisResult(
        kind="command",
        command="ls",
        explanation="Lists files.",
    )
    mock = mocker.patch("jwshell.cli.analyze", return_value=fake)
    result = runner.invoke(app, ["-v", "ls"])
    assert result.exit_code == 0, result.stderr
    assert mock.call_args.kwargs["verbose"] is True


def test_model_flag_overrides_config(with_env: None, mocker: MockerFixture) -> None:
    fake = AnalysisResult(
        kind="command",
        command="ls",
        explanation="Lists files.",
    )
    mock = mocker.patch("jwshell.cli.analyze", return_value=fake)
    result = runner.invoke(app, ["--model", "openai/gpt-5.2", "ls"])
    assert result.exit_code == 0, result.stderr
    assert mock.call_args.kwargs["cfg"].model == "openai/gpt-5.2"


def test_jwshell_error_surfaces_friendly_message(with_env: None, mocker: MockerFixture) -> None:
    from jwshell.client import JwshellError

    mocker.patch("jwshell.cli.analyze", side_effect=JwshellError("boom"))
    result = runner.invoke(app, ["ls"])
    assert result.exit_code == 1
    assert "boom" in result.stderr


def test_openrouter_error_surfaces_friendly_message(with_env: None, mocker: MockerFixture) -> None:
    import httpx
    from openrouter.errors import OpenRouterError

    fake_response = httpx.Response(status_code=503, content=b"upstream down")
    mocker.patch(
        "jwshell.cli.analyze",
        side_effect=OpenRouterError("upstream down", fake_response),
    )
    result = runner.invoke(app, ["ls"])
    assert result.exit_code == 1
    assert "openrouter error" in result.stderr.lower()
    assert "upstream down" in result.stderr


@pytest.mark.parametrize("flag", ["-h", "--help"])
def test_help_flag(flag: str) -> None:
    result = runner.invoke(app, [flag])
    assert result.exit_code == 0
    assert "INPUT" in result.stdout
