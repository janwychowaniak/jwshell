"""Render an :class:`AnalysisResult` to the terminal using rich."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import Console
from rich.padding import Padding
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text

if TYPE_CHECKING:
    from jwshell.schema import AnalysisResult


def _command_block(command: str) -> Syntax:
    return Syntax(
        command,
        "bash",
        theme="ansi_dark",
        background_color="default",
        word_wrap=True,
    )


def render(result: AnalysisResult, *, console: Console | None = None) -> None:
    """Pretty-print *result* to the terminal (stdout)."""
    out = console or Console()

    if result.kind == "command":
        out.print(_command_block(result.command))
        out.print()
        out.print(Text(result.explanation))
    else:
        out.print(Padding(Text("Suggested command:", style="bold"), (0, 0, 1, 0)))
        out.print(Panel(_command_block(result.command), border_style="cyan", expand=False))
        out.print()
        out.print(Text(result.explanation))

    if result.notes.strip():
        out.print()
        out.print(Text("Notes: ", style="bold yellow"), end="")
        out.print(Text(result.notes))
