import json
import logging
from pathlib import Path

import click  # https://click.palletsprojects.com/

from .constants import DEFAULT_SECTION
from .constants import KEY_WORDS_SETTING
from .core import envs_to_dict
from .core import filter_keys_by_substring
from .core import mask_sensitive_data_in_file
from .core import save_dict_to_env_file
from .core import save_dict_to_json_file
from .core import unmask_sensitive_data_in_file
from .settings import config
from .settings import get_config_value_as_list

logger = logging.getLogger(__name__)


def silent_echo(*args, **kwargs):
    pass


def file_error():
    click.echo("Path is a file, not a directory. Please provide a directory.", err=True)


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

    key_words = get_config_value_as_list(config, DEFAULT_SECTION, KEY_WORDS_SETTING)

    click.echo(f"Extracting secrets from all .env files in {path}")
    target_envs = get_config_value_as_list(config, DEFAULT_SECTION, "envs")
    env_files = [path / file for file in target_envs]
    env = envs_to_dict(env_files)

    secrets_dict = filter_keys_by_substring(env, key_words)
    if format == "json":
        output_file = save_dict_to_json_file(secrets_dict, path / "secrets.json")
        click.echo(f"Secrets saved to {output_file}")
    elif format == "env":
        output_file = save_dict_to_env_file(secrets_dict, path / ".secrets")
        click.echo(f"Secrets saved to {output_file}")
    else:
        output_file1 = save_dict_to_json_file(secrets_dict, path / "secrets.json")
        output_file2 = save_dict_to_env_file(secrets_dict, path / ".secrets")
        if output_file1 and output_file2:
            click.echo(f"Secrets saved to {output_file1} and {output_file2}")
        else:
            click.echo("No secrets found to extract.", err=True)


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

    key_words = get_config_value_as_list(config, DEFAULT_SECTION, KEY_WORDS_SETTING)

    click.echo(f"Masking sensitive data in all .env files in {path}")
    target_envs = get_config_value_as_list(config, DEFAULT_SECTION, "envs")
    for file_path in target_envs:
        file = path / file_path
        if file.exists():
            click.echo(f"Masking sensitive data in {file}")
            mask_sensitive_data_in_file(file, key_words)


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

    key_words = get_config_value_as_list(config, DEFAULT_SECTION, KEY_WORDS_SETTING)

    # Ensure that the secrets file exists
    secret_env = path / ".secrets"
    secret_json = path / "secrets.json"
    if not secret_env.exists() and not secret_json.exists():
        click.echo(
            "No secrets file(s) found to unmask (.secrets or secrets.json).", err=True
        )
        return

    click.echo(f"Unmasking sensitive data in all .env files in {path}")
    target_envs = get_config_value_as_list(config, DEFAULT_SECTION, "envs")
    for file_path in target_envs:
        env_file = path / file_path
        if env_file.exists():
            click.echo(f"Unmasking sensitive data in {env_file}")
            if secret_env.exists():
                env = envs_to_dict([secret_env])
                filtered = filter_keys_by_substring(env, key_words)
            elif secret_json.exists():
                filtered = json.loads(secret_json.read_text())
            unmask_sensitive_data_in_file(env_file, filtered)


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
