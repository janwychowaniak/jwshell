# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`jwshell` is a small Python 3.12+ CLI that takes a single string and either explains it (when it
is a valid bash/zsh command) or generates a command (when it is a natural-language description).
It does this with a **single OpenRouter chat call** that returns structured JSON; classification
between the two modes is performed by the model, not in code.

## Common commands

`uv` is the canonical workflow tool. All commands assume `uv sync --group dev` has been run.

```sh
uv run ruff check .            # lint
uv run ruff format .           # format
uv run ruff format --check .   # CI's format check (do not auto-fix)
uv run mypy                    # strict type-check (config in pyproject.toml)
uv run pytest                  # full test suite
uv run pytest tests/test_cli.py::test_explains_a_command   # single test
uv build                       # build sdist + wheel into dist/
uv run pip-audit --skip-editable                            # dependency audit
```

Run the CLI locally without installing:

```sh
uv run jwshell "ls -la"
JWSHELL_OR_APIKEY=sk-or-... uv run jwshell -v "find . -name '*.py'"
```

`JWSHELL_OR_APIKEY` is **required** for any real invocation; tests stub it out.

## Architecture

The pipeline is intentionally linear and lives entirely in `src/jwshell/`:

```
cli.main → load_config → analyze → render
              (config)     (client)  (render)
```

Key boundaries:

- **`config.py`** — reads `JWSHELL_OR_APIKEY` / `JWSHELL_OR_MODEL` env vars (defaults to
  `anthropic/claude-haiku-4.5`). The `--model` CLI flag overrides the env var. Raises
  `ConfigError`, which the CLI converts to `exit 1`.
- **`prompts.py`** — assembles the system prompt. `_BASE` defines the contract (classify into
  `command` vs `description`, return JSON only); `_BRIEF` / `_VERBOSE` are toggled by the `-v`
  flag and only shape the `explanation` field, not the schema.
- **`schema.py`** — `AnalysisResult` is the Pydantic model (`extra="forbid"`, `frozen=True`) the
  LLM must return. `response_format()` builds OpenRouter's strict-JSON-schema payload. Note the
  custom `_strict_schema` helper: Pydantic does not emit `additionalProperties: false` and does
  not mark every property `required` by default — both are needed for OpenRouter's strict mode,
  so don't replace it with a plain `model.model_json_schema()` call.
- **`client.py`** — single function `analyze()`. One chat request, then
  `AnalysisResult.model_validate_json()` on the message content. Raises `JwshellError` for empty
  output or schema mismatch; lets `OpenRouterError` propagate so the CLI can label it.
- **`render.py`** — formats the result with `rich`. Branches on `result.kind`: a `command`
  result prints the command then the explanation inline; a `description` result wraps the
  generated command in a labelled panel.
- **`cli.py`** — Typer app with one command. Two distinct `try/except` blocks: config errors
  before the request, then `JwshellError` / `OpenRouterError` after — keep this split when
  adding new failure modes so the user sees the right prefix (`error:` vs `openrouter error:`).

`__version__` is read from installed package metadata via `importlib.metadata.version("jwshell")`,
so the version in `pyproject.toml` is the single source of truth — do not hardcode it elsewhere.

## Conventions worth knowing

- **Strict typing.** `mypy --strict` runs over both `src/` and `tests/`. `from __future__ import
  annotations` plus `if TYPE_CHECKING:` imports are used throughout to keep runtime imports
  minimal — preserve this pattern.
- **Ruff is configured aggressively** (`ANN`, `B`, `UP`, `SIM`, `RUF`, `PTH`, `N`, `TC`, `C4`).
  Tests are exempt from `ANN` only. `line-length = 100`, double quotes.
- **Pre-commit** runs `ruff --fix` and `ruff-format` (see `.pre-commit-config.yaml`).
- **Pytest** runs with `filterwarnings = ["error"]` — any warning fails the suite. New code that
  emits a `DeprecationWarning` will break tests until handled.
- **`pytest-mock`** is the mocking tool of choice; tests use the `with_env` / `no_env` fixtures
  from `tests/conftest.py` rather than touching `os.environ` directly.

## CI

`.github/workflows/ci.yml` runs five jobs on every push/PR: lint, typecheck, dependency audit,
build, and tests on Python 3.12 + 3.13. Match these locally before pushing. A separate
`release.yml` publishes to PyPI on tag pushes.
