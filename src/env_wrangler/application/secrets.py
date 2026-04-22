"""Application use-cases for env_wrangler."""

import json
from pathlib import Path

from env_wrangler.domain.secrets import filter_keys_by_substring
from env_wrangler.domain.secrets import remove_masked_values
from env_wrangler.infrastructure.files import envs_to_dict
from env_wrangler.infrastructure.files import mask_sensitive_data_in_file
from env_wrangler.infrastructure.files import save_dict_to_env_file
from env_wrangler.infrastructure.files import save_dict_to_json_file
from env_wrangler.infrastructure.files import unmask_sensitive_data_in_file


def extract_secrets(
    path: Path, key_words: list[str], target_envs: list[str], output_format: str | None
) -> list[Path]:
    """Extract secrets from env files and persist them in the requested format."""
    env_files = [str(path / file) for file in target_envs]
    env = envs_to_dict(env_files)

    secrets_dict = filter_keys_by_substring(env, key_words)
    secrets_dict = remove_masked_values(secrets_dict)

    if not secrets_dict:
        return []

    if output_format == "json":
        output_file = save_dict_to_json_file(secrets_dict, path / "secrets.json")
        return [output_file] if output_file else []

    if output_format == "env":
        output_file = save_dict_to_env_file(secrets_dict, path / ".secrets")
        return [output_file] if output_file else []

    output_file1 = save_dict_to_json_file(secrets_dict, path / "secrets.json")
    output_file2 = save_dict_to_env_file(secrets_dict, path / ".secrets")
    return [file for file in (output_file1, output_file2) if file]


def mask_secrets(
    path: Path, key_words: list[str], ignore_keys: list[str], target_envs: list[str]
) -> list[Path]:
    """Mask sensitive values in configured env files."""
    masked_files: list[Path] = []
    for file_path in target_envs:
        file = path / file_path
        if file.exists():
            masked_files.append(file)
            mask_sensitive_data_in_file(file, key_words, ignore_keys)

    return masked_files


def unmask_secrets(
    path: Path, key_words: list[str], target_envs: list[str]
) -> list[Path]:
    """Unmask sensitive values in configured env files."""
    secret_env = path / ".secrets"
    secret_json = path / "secrets.json"

    filtered: dict[str, str]
    if secret_env.exists():
        env = envs_to_dict([str(secret_env)])
        filtered = filter_keys_by_substring(env, key_words)
    else:
        filtered = json.loads(secret_json.read_text())

    unmasked_files: list[Path] = []
    for file_path in target_envs:
        env_file = path / file_path
        if env_file.exists():
            unmasked_files.append(env_file)
            unmask_sensitive_data_in_file(env_file, filtered)

    return unmasked_files


def has_secrets_file(path: Path) -> bool:
    """Return True when either supported secrets file exists."""
    return (path / ".secrets").exists() or (path / "secrets.json").exists()
