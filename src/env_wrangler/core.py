import json
from pathlib import Path

from dotenv import dotenv_values


def envs_to_dict(env_files: list[str]) -> dict:
    """Read env files, merge them and return a dict"""
    config = {}
    for env_file in env_files:
        config |= dotenv_values(env_file)
    return config


def save_dict_to_json_file(data: dict, file_path: Path) -> Path:
    """Save a dictionary to a JSON file."""
    if not data:
        return None
    file_path = Path(file_path).expanduser()
    file_path.write_text(json.dumps(data, indent=2))
    return file_path


def save_dict_to_env_file(data: dict, file_path: str) -> Path:
    """Save a dictionary to an env file."""
    if not data:
        return None
    env_content = "\n".join([f"{key}={value}" for key, value in data.items()])
    file_path = Path(file_path).expanduser()
    file_path.write_text(env_content)
    return file_path


def filter_keys_by_substring(input_dict: dict, words_to_keep: list[str]) -> dict:
    """
    Filters a dictionary to keep only keys that include any of the specified words.

    :param input_dict: Dictionary to be filtered.
    :param words_to_keep: List of words to check against the keys in the dictionary.
    """
    secrets = {
        key: input_dict[key]
        for key in input_dict
        if any(word in key for word in words_to_keep)
    }
    # Remove any keys with values of "********"
    # Safeguard to prevent extracting masked values
    return {key: value for key, value in secrets.items() if value != "********"}


def mask_sensitive_data_in_file(file_path: str, filter_keys: list) -> Path:
    """Mask sensitive data in a .env file.

    Args:
        file_path (str): The path to the .env file.
        filter_keys (list): The keys to mask in the .env file.
    """
    file_path = Path(file_path).expanduser()
    lines = file_path.read_text().splitlines()

    masked_lines = []
    for line in lines:
        for key in filter_keys:
            if key in line.split("=")[0]:
                line = line.split("=")[0] + "=********"  # noqa: PLW2901
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
            if key in line.split("=")[0]:
                line = line.split("=")[0] + "=" + value  # noqa: PLW2901
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
