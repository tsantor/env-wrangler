# -----------------------------------------------------------------------------
# Generate help output when running just `make`
# -----------------------------------------------------------------------------
.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:
	@python3 -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

# -----------------------------------------------------------------------------
# Variables
# -----------------------------------------------------------------------------

python_version=3.13.2
venv=env-wrangler_env
package_name=env-wrangler
aws_profile=xstudios
s3_bucket=xstudios-pypi

# START - Generic commands
# -----------------------------------------------------------------------------
# Environment
# -----------------------------------------------------------------------------

env:  ## Create virtual environment (uses `uv`)
	uv venv --python ${python_version}

env_remove:  ## Remove virtual environment
	rm -rf .venv

env_from_scratch: env_remove env pip_install  ## Create environment from scratch

# -----------------------------------------------------------------------------
# Pip
# -----------------------------------------------------------------------------

pip_install:  ## Install requirements
	uv pip install --upgrade pip
	@for file in $$(ls requirements/*.txt); do \
			uv pip install -r $$file; \
	done
	pre-commit install

pip_add_dependencies:  ## Add dependencies
	uv add toml click python-dotenv

pip_add_dev_dependencies:  ## Add dev dependencies
	uv add twine wheel build ruff pipdeptree pre-commit --group dev

pip_add_test_dependencies:  ## Add test dependencies
	uv add pytest pytest-cov pytest-mock coverage --group test

pip_install_editable:  ## Install in editable mode
	uv pip install -e .
	uv sync --all-groups
	pre-commit install

pip_list:  ## Run pip list
	uv pip list

pip_tree: ## Run pip tree
	uv pip tree

pipdeptree:  ## # Run pipdeptree
	uv run pipdeptree

uv_sync:  ## Sync dependencies [production, dev, test]
	uv sync --all-groups

uv_lock_check:	## Check if lock file is up to date
	uv lock --check

# -----------------------------------------------------------------------------
# Testing
# -----------------------------------------------------------------------------

pytest:  ## Run tests
	pytest -vx

pytest_verbose:  ## Run tests in verbose mode
	pytest -vvs

pytest_node_ids:  ## show node ids
	cat .pytest_cache/v/cache/nodeids

coverage:  ## Run tests with coverage
	coverage run -m pytest && coverage html

coverage_verbose:  ## Run tests with coverage in verbose mode
	coverage run -m pytest -vss && coverage html

coverage_skip:  ## Run tests with coverage and skip covered
	coverage run -m pytest -vs && coverage html --skip-covered

open_coverage:  ## Open coverage report
	open htmlcov/index.html

# -----------------------------------------------------------------------------
# Ruff
# -----------------------------------------------------------------------------

ruff_format: ## Run ruff format
	ruff format src/env_wrangler

ruff_check: ## Run ruff check
	ruff check src/env_wrangler

ruff_clean: ## Run ruff clean
	ruff clean

# -----------------------------------------------------------------------------
# Cleanup
# -----------------------------------------------------------------------------

clean_build:  ## Remove build artifacts
	rm -fr build/ dist/ .eggs/
	find . -name '*.egg-info' -o -name '*.egg' -exec rm -fr {} +

clean_pyc:  ## Remove python file artifacts
	find . \( -name '*.pyc' -o -name '*.pyo' -o -name '*~' -o -name '__pycache__' \) -exec rm -fr {} +

clean: clean_build clean_pyc ## Remove all build and python artifacts

clean_pytest_cache:  ## Clear pytest cache
	rm -rf .pytest_cache

clean_ruff_cache:  ## Clear ruff cache
	rm -rf .ruff_cache

clean_tox_cache:  ## Clear tox cache
	rm -rf .tox

clean_coverage:  ## Clear coverage cache
	rm .coverage
	rm -rf htmlcov

clean_tests: clean_pytest_cache clean_ruff_cache clean_tox_cache clean_coverage  ## Clear pytest, ruff, tox, and coverage caches

# -----------------------------------------------------------------------------
# Miscellaneous
# -----------------------------------------------------------------------------

tree:  ## Show directory tree
	tree -I 'build|dist|htmlcov|node_modules|migrations|contrib|__pycache__|*.egg-info|staticfiles|media|django_project'

# -----------------------------------------------------------------------------
# Deploy
# -----------------------------------------------------------------------------

dist: clean  ## Builds source and wheel package
	python3 -m build

release_test: dist  ## Upload package to pypi test
	twine upload dist/* -r pypitest

release: dist  ## Package and upload a release
	twine upload dist/*

check: dist  ## Twine check
	twine check dist/*

# -----------------------------------------------------------------------------
# X Studios S3 PyPi
# -----------------------------------------------------------------------------

create_latest_copy: dist  ## Create latest copy of distro
	cp dist/*.whl dist/${package_name}-latest-py3-none-any.whl

push_to_s3: create_latest_copy  ## Push distro to S3 bucket
	aws s3 sync --profile=${aws_profile} --acl public-read ./dist/ s3://${s3_bucket}/ \
        --exclude "*" --include "*.whl"
	echo "https://${s3_bucket}.s3.amazonaws.com/${package_name}-latest-py3-none-any.whl"

# END - Generic commands
# -----------------------------------------------------------------------------
# Project Specific
# -----------------------------------------------------------------------------

# Add your project specific commands here
