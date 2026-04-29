"""Typer CLI entry point for jwshell."""

from __future__ import annotations

from typing import Annotated

import typer
from openrouter.errors import OpenRouterError
from rich.console import Console

from jwshell import __version__
from jwshell.client import JwshellError, analyze
from jwshell.config import ConfigError, load_config
from jwshell.render import render

app = typer.Typer(
    name="jwshell",
    help=("Explain a shell command, or generate one from a description. Powered by OpenRouter."),
    add_completion=False,
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)

_err_console = Console(stderr=True)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"jwshell {__version__}")
        raise typer.Exit


@app.command()
def main(
    text: Annotated[
        str,
        typer.Argument(
            metavar="INPUT",
            help="A bash/zsh command to explain, or a description of what you want to do.",
            show_default=False,
        ),
    ],
    verbose: Annotated[
        bool,
        typer.Option(
            "-v",
            "--verbose",
            help="Produce a detailed, per-flag explanation.",
        ),
    ] = False,
    model: Annotated[
        str | None,
        typer.Option(
            "--model",
            metavar="MODEL",
            help="OpenRouter model id (overrides JWSHELL_OR_MODEL).",
            show_default=False,
        ),
    ] = None,
    _version: Annotated[
        bool,
        typer.Option(
            "--version",
            callback=_version_callback,
            is_eager=True,
            help="Show jwshell version and exit.",
        ),
    ] = False,
) -> None:
    """Run jwshell on INPUT and print the result."""
    try:
        cfg = load_config(model_override=model)
    except ConfigError as exc:
        _err_console.print(f"[red]error:[/red] {exc}")
        raise typer.Exit(1) from exc

    try:
        result = analyze(text, verbose=verbose, cfg=cfg)
    except JwshellError as exc:
        _err_console.print(f"[red]error:[/red] {exc}")
        raise typer.Exit(1) from exc
    except OpenRouterError as exc:
        _err_console.print(f"[red]openrouter error:[/red] {exc}")
        raise typer.Exit(1) from exc

    render(result)
