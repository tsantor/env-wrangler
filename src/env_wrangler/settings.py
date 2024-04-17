import logging
import shutil
from configparser import ConfigParser
from pathlib import Path

import pkg_resources

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------


def copy_resource_file(filename, dst):
    """Copy data files from package data folder."""
    # Create destination dir if needed
    dir_path = Path(dst).parent
    if not dir_path.is_dir():
        dir_path.mkdir()

    # Copy data file to destination
    src = pkg_resources.resource_filename("env_wrangler", f"data/{filename}")
    dst = str(Path(dir_path).expanduser())
    shutil.copy2(src, dst)


CONFIG_FILE = Path("~/.env-wrangler/env-wrangler.cfg").expanduser()
if not CONFIG_FILE.exists():
    copy_resource_file("env-wrangler.cfg", str(CONFIG_FILE))  # pragma: no cover

LOG_FILE = Path("~/.env-wrangler/env-wrangler.log").expanduser()
if not LOG_FILE.exists():
    LOG_FILE.touch()  # pragma: no cover

# -----------------------------------------------------------------------------


def get_config_value_as_list(config: ConfigParser, section: str, key: str) -> list[str]:
    data_string = config[section][key]
    return [item.strip() for item in data_string.split(",")]


config = ConfigParser()
config.read(CONFIG_FILE)
