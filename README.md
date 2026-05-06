# jwshell

[![PyPI version](https://img.shields.io/pypi/v/jwshell.svg)](https://pypi.org/project/jwshell/)

LLM-powered shell command explainer and generator.

`jwshell` takes a single string and either:

- **explains** it, when the string is a valid bash/zsh command or expression, or
- **generates** a command, when the string is a natural-language description of a
  desired effect.

It uses [OpenRouter](https://openrouter.ai/) under the hood.

## Install

Requires Python 3.12+.

```sh
uv tool install jwshell    # recommended
pipx install jwshell       # alternative
pip install jwshell        # plain pip
```

## Configure

```sh
export JWSHELL_OR_APIKEY="sk-or-..."        # required
export JWSHELL_OR_MODEL="openai/gpt-5.2"    # optional, defaults to anthropic/claude-haiku-4.5
```

## Use

Explain a command (brief):

```sh
jwshell "ls -la"
```

Explain a command in detail:

```sh
jwshell -v "find . -name '*.py' -mtime -1"
```

Generate a command from a description:

```sh
jwshell "list every python file modified today"
```

Override the model for a single call:

```sh
jwshell --model anthropic/claude-sonnet-4.6 "tar all logs older than 7 days"
```

## Development

```sh
git clone https://github.com/janwychowaniak/jwshell.git
cd jwshell
uv sync               # install runtime + dev deps
pre-commit install    # optional: ruff lint + format on commit

uv run ruff check .   # lint
uv run ruff format .  # format
uv run mypy           # strict type-check
uv run pytest         # tests
```

## License

MIT — see [LICENSE](LICENSE).
