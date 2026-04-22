# Env Wrangler

![Coverage](https://img.shields.io/badge/coverage-99.53%25-brightgreen)

## Overview

Extract secrets from .env files into their own file (either `.secrets` or `secrets.json`). Also provides `mask` and `unmask` options. The resulting secrets file can be leveraged to get your secrets into a 3rd party secrets manager like AWS Secrets Manager or something else.

Plays nice with [cookiecutter-django](https://github.com/cookiecutter/cookiecutter-django).

## Installation

Core/library install:

```bash
uv add env-wrangler
```

CLI install:

```bash
uv add "env-wrangler[cli]"
```

## Usage

The `path` parameter is a directory, not a file!

```bash
env-wrangler extract --path ".envs/.production"
# Only run if you've previously run extract
env-wrangler mask --path ".envs/.production"
env-wrangler unmask --path ".envs/.production"
```

> **NOTE:** For help run `env-wrangler --help` or for a specific command run `env-wrangler {command} --help`.

On first run, `env-wrangler` creates `~/.env-wrangler/env-wrangler.toml`.
The default config section supports:

- `key_words`: substrings used to identify secret-like keys
- `ignore_keys`: exact keys to skip even if they match `key_words`
- `envs`: env files to scan (for example `.env`, `.django`, `.postgres`)

## Development

```bash
just --list
just env
just pip-install-editable
```

Architecture guardrails:

- [DDD / Clean Architecture Guardrails](docs/architecture.md)

## Testing

```bash
just pytest
just coverage
just open-coverage
```

For quick local quality checks:

```bash
just check
```

## Issues

If you experience any issues, please create one in the
[issue tracker](https://bitbucket.org/tsantor/env-wrangler/issues).
