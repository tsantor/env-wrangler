import logging
from pathlib import Path

import click  # https://click.palletsprojects.com/

from .core import envs_to_dict
from .core import filter_keys_by_substring
from .core import mask_sensitive_data_in_file
from .core import replace_values_in_file
from .core import save_dict_to_env_file
from .core import save_dict_to_json_file
from .settings import config
from .settings import get_config_value_as_list

logger = logging.getLogger(__name__)


def common_options(func):
    """Decorator to add common options to a command."""
    func = click.option(
        "-p", "--path", required=True, type=click.Path(), help="Path to the .env file"
    )(func)
    return click.option("-v", "--verbose", count=True, help="Set the verbosity level.")(
        func
    )


@click.command()
@common_options
@click.option(
    "--format",
    type=click.Choice(["both", "json", "env"], case_sensitive=False),
    help="The output format.",
)
def extract(path, verbose, format):
    """Extract secrets from the .env file into a separate file."""
    project_path = Path(path).expanduser()
    words = get_config_value_as_list(config, "default", "key_words")

    # Env dirs
    # local_env_dir = project_path / ".envs/.local"
    prod_env_dir = project_path / ".envs/.production"

    prod_env_files = [prod_env_dir / ".django", prod_env_dir / ".postgres"]
    prod_config = envs_to_dict(prod_env_files)
    # print(prod_config)
    final_prod_config = filter_keys_by_substring(prod_config, words)
    # print(final_prod_config)

    # Output as json or env
    if format == "json":
        save_dict_to_json_file(final_prod_config, prod_env_dir / "secrets.json")
    elif format == "env":
        save_dict_to_env_file(final_prod_config, prod_env_dir / ".secrets")
    else:
        save_dict_to_json_file(final_prod_config, prod_env_dir / "secrets.json")
        save_dict_to_env_file(final_prod_config, prod_env_dir / ".secrets")


@click.command()
@common_options
def mask(path, verbose) -> None:
    """Mask sensitive data in the .env file."""
    env_file = Path(path).expanduser()
    key_words = get_config_value_as_list(config, "default", "key_words")
    mask_sensitive_data_in_file(env_file, key_words)


@click.command()
@common_options
def unmask(path, verbose) -> None:
    """Unmask sensitive data in the .env file."""
    env_file = Path(path).expanduser()
    key_words = get_config_value_as_list(config, "default", "key_words")
    secret_env = env_file.parent / ".secrets"
    env = envs_to_dict([secret_env])
    filtered = filter_keys_by_substring(env, key_words)
    replace_values_in_file(env_file, filtered)


# Set up your command-line interface grouping
@click.group()
@click.version_option()
def cli():
    """Extract secrets from .env files into their own file(s) for use in a 3rd party secrets manager"""


cli.add_command(extract)
cli.add_command(mask)
cli.add_command(unmask)

if __name__ == "__main__":
    cli()
