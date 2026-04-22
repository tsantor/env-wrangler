import logging
from pathlib import Path

import click

from .application.secrets import extract_secrets
from .application.secrets import has_secrets_file
from .application.secrets import mask_secrets
from .application.secrets import unmask_secrets
from .infrastructure.config import config
from .infrastructure.paths import home_agnostic_path

logger = logging.getLogger(__name__)


def file_error():
    click.secho(
        "Path is a file, not a directory. Please provide a directory.",
        fg="red",
        err=True,
    )


def common_options(func):
    """Decorator to add common options to a command."""
    return click.option(
        "-p",
        "--path",
        required=True,
        type=click.Path(),
        help="Path to the .env file or a directory containing .env files.",
    )(func)


@click.command()
@common_options
@click.option(
    "--format",
    type=click.Choice(["both", "json", "env"], case_sensitive=False),
    help="The output format.",
)
def extract(path, format):  # noqa: A002
    """Extract secrets from the .env file(s) in the given directory into a separate file."""

    path = Path(path).expanduser()
    if path.is_file():
        file_error()
        return

    click.echo(f"Extracting secrets from all .env files in {home_agnostic_path(path)}")

    key_words = config["default"]["key_words"]
    target_envs = config["default"]["envs"]
    output_files = extract_secrets(path, key_words, target_envs, format)
    if not output_files:
        click.secho("No secrets found to extract.", err=True, fg="yellow")
        return

    for output_file in output_files:
        click.echo(f"Secrets saved to {home_agnostic_path(output_file)}")


@click.command()
@common_options
def mask(path) -> None:
    """Mask sensitive data in the .env file(s) in the given directory."""

    path = Path(path).expanduser()
    if path.is_file():
        file_error()
        return

    if not has_secrets_file(path):
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

    masked_files = mask_secrets(
        path,
        config["default"]["key_words"],
        config["default"]["ignore_keys"],
        config["default"]["envs"],
    )

    # Let the user know which files were masked
    if masked_files:
        click.echo("Masked sensitive data in the following envs:")
        for file in masked_files:
            click.echo(f"   {home_agnostic_path(file)}")


@click.command()
@common_options
def unmask(path) -> None:
    """Unmask sensitive data in the .env file(s) in the given directory."""

    path = Path(path).expanduser()
    if path.is_file():
        file_error()
        return

    if not has_secrets_file(path):
        click.secho(
            "No secrets file(s) found (.secrets or secrets.json).",
            fg="yellow",
            err=True,
        )
        return

    unmasked_files = unmask_secrets(
        path,
        config["default"]["key_words"],
        config["default"]["envs"],
    )

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
