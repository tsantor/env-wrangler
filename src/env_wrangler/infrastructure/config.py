"""Infrastructure helpers for configuration loading."""

import importlib.resources as importlib_resources
import logging
import shutil
import tomllib
from pathlib import Path

logger = logging.getLogger(__name__)


def copy_resource_file(filename: str, dst: str) -> None:
    """Copy data files from package data folder using importlib.resources."""
    dir_path = Path(dst).parent
    if not dir_path.is_dir():
        dir_path.mkdir(parents=True, exist_ok=True)

    src_path = importlib_resources.files("env_wrangler.data").joinpath(filename)
    with src_path.open("rb") as src_file, Path(dst).open("wb") as dst_file:
        shutil.copyfileobj(src_file, dst_file)


CONFIG_FILE = Path("~/.env-wrangler/env-wrangler.toml").expanduser()
if not CONFIG_FILE.exists():
    copy_resource_file("env-wrangler.toml", str(CONFIG_FILE))  # pragma: no cover

LOG_FILE = Path("~/.env-wrangler/env-wrangler.log").expanduser()
if not LOG_FILE.exists():
    LOG_FILE.touch()  # pragma: no cover

with CONFIG_FILE.open("rb") as f:
    config = tomllib.load(f)
