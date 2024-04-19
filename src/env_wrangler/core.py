import json
from pathlib import Path

from dotenv import dotenv_values

from .constants import MASK_VALUE


def envs_to_dict(env_files: list[str]) -> dict:
    """Read env files, merge them and return a dict"""
    config = {}
    for env_file in env_files:
        config |= dotenv_values(env_file)
    return config


def save_dict_to_json_file(data: dict, file_path: Path) -> Path:
    """Save a dictionary to a JSON file (non-destructive)."""
    if not data:
        return None
    file_path = Path(file_path).expanduser()
    if file_path.exists():
        existing_data = json.loads(file_path.read_text())
        existing_data.update(data)
        data = existing_data
    # We ensure it is sorted before writing
    file_path.write_text(json.dumps(data, indent=2, sort_keys=True))
    return file_path


def save_dict_to_env_file(data: dict, file_path: str) -> Path:
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
    # We ensure it is sorted before writing
    env_content = "\n".join([f"{key}={value}" for key, value in sorted(data.items())])
    file_path.write_text(env_content)
    return file_path


def filter_keys_by_substring(input_dict: dict, words_to_keep: list[str]) -> dict:
    """
    Filters a dictionary to keep only keys that include any of the specified words.

    :param input_dict: Dictionary to be filtered.
    :param words_to_keep: List of words to check against the keys in the dictionary.
    """
    return {
        key: input_dict[key]
        for key in input_dict
        if any(word in key for word in words_to_keep)
    }


def remove_masked_values(input_dict: dict) -> dict:
    """
    Filters a dictionary to remove masked values.

    :param input_dict: Dictionary to be filtered.
    """
    return {key: value for key, value in input_dict.items() if value != MASK_VALUE}


def mask_sensitive_data_in_file(
    file_path: str, filter_keys: list, ignore_keys=None
) -> Path:
    """Mask sensitive data in a .env file.

    Args:
        file_path (str): The path to the .env file.
        filter_keys (list): The keys to mask in the .env file.
    """
    file_path = Path(file_path).expanduser()
    lines = file_path.read_text().splitlines()

    ignore_keys = ignore_keys or []

    masked_lines = []
    for line in lines:
        for check_key in filter_keys:
            key = line.split("=", 1)[0]
            if check_key in key and key not in ignore_keys:
                line = key + f"={MASK_VALUE}"  # noqa: PLW2901
        masked_lines.append(line)

    file_path.write_text("\n".join(masked_lines))
    return file_path


def unmask_sensitive_data_in_file(file_path: str, replacements: dict) -> Path:
    """Unmask sensitive data in a .env file.

    Args:
        file_path (str): The path to the file.
        replacements (dict): The dictionary of key-value pairs.
    """
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


def json_to_env(json_file_path: str, env_file_path: str) -> Path:
    """Convert a JSON file to a .env file.

    Args:
        json_file_path (str): The path to the JSON file.
        env_file_path (str): The path to the .env file.
    """
    json_file_path = Path(json_file_path).expanduser()
    env_file_path = Path(env_file_path).expanduser()

    with json_file_path.open("r") as json_file:
        data = json.load(json_file)

    env_lines = [f"{key}={value}" for key, value in data.items()]
    env_file_path.write_text("\n".join(env_lines))
    return env_file_path
