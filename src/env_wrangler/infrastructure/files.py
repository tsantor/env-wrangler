"""Infrastructure helpers for file IO."""

import json
from pathlib import Path

from dotenv import dotenv_values


def envs_to_dict(env_files: list[str]) -> dict:
    """Read env files, merge them and return a dict."""
    config = {}
    for env_file in env_files:
        config |= dotenv_values(env_file)
    return config


def save_dict_to_json_file(data: dict, file_path: Path | str) -> Path | None:
    """Save a dictionary to a JSON file (non-destructive)."""
    if not data:
        return None

    file_path = Path(file_path).expanduser()
    if file_path.exists():
        existing_data = json.loads(file_path.read_text())
        existing_data.update(data)
        data = existing_data

    file_path.write_text(json.dumps(data, indent=2, sort_keys=True))
    return file_path


def save_dict_to_env_file(data: dict, file_path: Path | str) -> Path | None:
    """Save a dictionary to an env file (non-destructive)."""
    if not data:
        return None

    file_path = Path(file_path).expanduser()
    if file_path.exists():
        existing_data = dict(
            line.split("=", 1) for line in file_path.read_text().splitlines() if line
        )
        existing_data.update(data)
        data = existing_data

    env_content = "\n".join([f"{key}={value}" for key, value in sorted(data.items())])
    file_path.write_text(env_content)
    return file_path


def mask_sensitive_data_in_file(
    file_path: str | Path, filter_keys: list[str], ignore_keys: list[str] | None = None
) -> Path:
    """Mask sensitive data in an env file."""
    file_path = Path(file_path).expanduser()
    lines = file_path.read_text().splitlines()

    ignore_keys = ignore_keys or []

    masked_lines = []
    for line in lines:
        for check_key in filter_keys:
            key = line.split("=", 1)[0]
            if check_key in key and key not in ignore_keys:
                line = key + "=********"  # noqa: PLW2901
        masked_lines.append(line)

    file_path.write_text("\n".join(masked_lines))
    return file_path


def unmask_sensitive_data_in_file(file_path: str | Path, replacements: dict) -> Path:
    """Unmask sensitive data in an env file."""
    file_path = Path(file_path).expanduser()
    lines = file_path.read_text().splitlines()

    replaced_lines = []
    for line in lines:
        for key, value in replacements.items():
            if key in line.split("=", 1)[0]:
                line = line.split("=", 1)[0] + "=" + value  # noqa: PLW2901
        replaced_lines.append(line)

    file_path.write_text("\n".join(replaced_lines))
    return file_path


def json_to_env(json_file_path: str | Path, env_file_path: str | Path) -> Path:
    """Convert a JSON file to an env file."""
    json_file_path = Path(json_file_path).expanduser()
    env_file_path = Path(env_file_path).expanduser()

    with json_file_path.open("r") as json_file:
        data = json.load(json_file)

    env_lines = [f"{key}={value}" for key, value in data.items()]
    env_file_path.write_text("\n".join(env_lines))
    return env_file_path
