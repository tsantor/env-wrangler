# Env Wrangler

![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)

## Overview

Extract secrets from .env files into their own file (either `.secrets` or `secrets.json`). Also provides `mask` and `unmask` options. The resulting secrets file can be leveraged to get your secrets into a 3rd party secrets manager like AWS Secrets Manager or something else.

Plays nice with [cookiecutter-django](https://github.com/cookiecutter/cookiecutter-django).

## Installation

```bash
python3 -m pip install env-wrangler
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

Upon first run, `env-wrangler` creates a `~/.env-wrangler/env-wrangler.toml` file. You can modify this to add/remove key words based on your needs.

## Development

```bash
make env
make pip_install
make pip_install_editable
```

## Testing

```bash
make pytest
make coverage
make open_coverage
```

# TODO
- Add tests for cli commands
- Write secrets to file non-destructively (eg - add key if not there, remove key if no longer present)

## Issues

If you experience any issues, please create an [issue](https://github.com/tsantor/env-wrangler/issues) on Github.
