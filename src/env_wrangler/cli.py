import json
import logging
from pathlib import Path

import click  # https://click.palletsprojects.com/

from .constants import DEFAULT_SECTION
from .constants import ENVS_SETTING
from .constants import IGNORE_KEYS_SETTING
from .constants import KEY_WORDS_SETTING
from .core import envs_to_dict
from .core import filter_keys_by_substring
from .core import mask_sensitive_data_in_file
from .core import remove_masked_values
from .core import save_dict_to_env_file
from .core import save_dict_to_json_file
from .core import unmask_sensitive_data_in_file
from .settings import config
from .utils import home_agnostic_path

logger = logging.getLogger(__name__)


def silent_echo(*args, **kwargs):
    pass


def file_error():
    click.secho(
        "Path is a file, not a directory. Please provide a directory.",
        fg="red",
        err=True,
    )


def common_options(func):
    """Decorator to add common options to a command."""
    func = click.option(
        "-p",
        "--path",
        required=True,
        type=click.Path(),
        help="Path to the .env file or a directory containing .env files.",
    )(func)
    return click.option("--verbose", is_flag=True, help="Enables verbose mode.")(func)


@click.command()
@common_options
@click.option(
    "--format",
    type=click.Choice(["both", "json", "env"], case_sensitive=False),
    help="The output format.",
)
def extract(path, verbose, format):  # noqa: A002
    """Extract secrets from the .env file(s) in the given directory into a separate file."""

    if not verbose:
        click.echo = silent_echo

    path = Path(path).expanduser()
    if path.is_file():
        file_error()
        return

    click.echo(f"Extracting secrets from all .env files in {home_agnostic_path(path)}")

    key_words = config[DEFAULT_SECTION][KEY_WORDS_SETTING]
    target_envs = config[DEFAULT_SECTION][ENVS_SETTING]
    env_files = [path / file for file in target_envs]
    env = envs_to_dict(env_files)

    secrets_dict = filter_keys_by_substring(env, key_words)
    secrets_dict = remove_masked_values(secrets_dict)

    if not secrets_dict:
        click.secho("No secrets found to extract.", err=True, fg="yellow")
        return

    if format == "json":
        output_file = save_dict_to_json_file(secrets_dict, path / "secrets.json")
        click.echo(f"Secrets saved to {home_agnostic_path(output_file)}")
    elif format == "env":
        output_file = save_dict_to_env_file(secrets_dict, path / ".secrets")
        click.echo(f"Secrets saved to {home_agnostic_path(output_file)}")
    else:
        output_file1 = save_dict_to_json_file(secrets_dict, path / "secrets.json")
        output_file2 = save_dict_to_env_file(secrets_dict, path / ".secrets")
        click.echo(f"Secrets saved to {home_agnostic_path(output_file1)}")
        click.echo(f"Secrets saved to {home_agnostic_path(output_file2)}")


@click.command()
@common_options
def mask(path, verbose) -> None:
    """Mask sensitive data in the .env file(s) in the given directory."""

    if not verbose:
        click.echo = silent_echo

    path = Path(path).expanduser()
    if path.is_file():
        file_error()
        return

    # Ensure that the secrets file exists
    secret_env = path / ".secrets"
    secret_json = path / "secrets.json"
    if not secret_env.exists() and not secret_json.exists():
        click.secho(
            (
                "No secrets file(s) found (.secrets or secrets.json). "
                "If you have not extracted secrets, please run 'extract' first.\n"
                "This prevents mistakenly masking all values in the .env file(s) without a backup."
            ),
            fg="yellow",
            err=True,
        )
        return

    key_words = config[DEFAULT_SECTION][KEY_WORDS_SETTING]
    ignore_keys = config[DEFAULT_SECTION][IGNORE_KEYS_SETTING]
    target_envs = config[DEFAULT_SECTION][ENVS_SETTING]

    masked_files = []
    for file_path in target_envs:
        file = path / file_path
        if file.exists():
            masked_files.append(file)
            mask_sensitive_data_in_file(file, key_words, ignore_keys)

    # Let the user know which files were masked
    if masked_files:
        click.echo("Masked sensitive data in the following envs:")
        for file in masked_files:
            click.echo(f"   {home_agnostic_path(file)}")


@click.command()
@common_options
def unmask(path, verbose) -> None:
    """Unmask sensitive data in the .env file(s) in the given directory."""

    if not verbose:
        click.echo = silent_echo

    path = Path(path).expanduser()
    if path.is_file():
        file_error()
        return

    # Ensure that the secrets file exists
    secret_env = path / ".secrets"
    secret_json = path / "secrets.json"
    if not secret_env.exists() and not secret_json.exists():
        click.secho(
            "No secrets file(s) found (.secrets or secrets.json).",
            fg="yellow",
            err=True,
        )
        return

    key_words = config[DEFAULT_SECTION][KEY_WORDS_SETTING]
    target_envs = config[DEFAULT_SECTION][ENVS_SETTING]

    unmasked_files = []
    for file_path in target_envs:
        env_file = path / file_path
        if env_file.exists():
            unmasked_files.append(env_file)
            if secret_env.exists():
                env = envs_to_dict([secret_env])
                filtered = filter_keys_by_substring(env, key_words)
            elif secret_json.exists():
                filtered = json.loads(secret_json.read_text())
            unmask_sensitive_data_in_file(env_file, filtered)

    # Let the user know which files were unmasked
    if unmasked_files:
        click.echo("Unmasked sensitive data in the following envs:")
        for file in unmasked_files:
            click.echo(f"   {home_agnostic_path(file)}")


# Set up your command-line interface grouping
@click.group()
@click.version_option()
def cli():
    """Extract secrets from .env files into their own file(s) for use in a
    3rd party secrets manager."""


cli.add_command(extract)
cli.add_command(mask)
cli.add_command(unmask)

if __name__ == "__main__":
    cli()
