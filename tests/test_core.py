import json
from pathlib import Path

from dotenv import dotenv_values
from env_wrangler.core import envs_to_dict
from env_wrangler.core import filter_keys_by_substring
from env_wrangler.core import mask_sensitive_data_in_file
from env_wrangler.core import save_dict_to_env_file
from env_wrangler.core import save_dict_to_json_file


def test_envs_to_dict(tmp_path):
    # Create two .env files in the temporary directory
    (tmp_path / "file1.env").write_text("KEY1=VALUE1\nKEY2=VALUE2")
    (tmp_path / "file2.env").write_text("KEY3=VALUE3\nKEY4=VALUE4")

    # Call envs_to_dict with the paths to the .env files
    result = envs_to_dict([str(tmp_path / "file1.env"), str(tmp_path / "file2.env")])

    # Check that the result is a dictionary with the correct key-value pairs
    assert result == {
        "KEY1": "VALUE1",
        "KEY2": "VALUE2",
        "KEY3": "VALUE3",
        "KEY4": "VALUE4",
    }


def test_save_dict_to_json_file(tmp_path):
    data = {"key1": "value1", "key2": "value2"}
    file_path = tmp_path / "test.json"
    save_dict_to_json_file(data, str(file_path))

    file_path = Path(file_path)
    loaded_data = json.loads(file_path.read_text())

    assert loaded_data == data


def test_save_dict_to_env_file(tmp_path):
    data = {"key1": "value1", "key2": "value2"}
    file_path = tmp_path / "test.env"
    save_dict_to_env_file(data, str(file_path))

    file_path = Path(file_path)
    lines = file_path.read_text().splitlines()

    loaded_data = {}
    for line in lines:
        key, value = line.split("=")
        loaded_data[key] = value

    assert loaded_data == data


def test_filter_keys_by_substring():
    input_dict = {
        "ACCESS_KEY": "my-access-key",
        "ACCESS_TOKEN": "my-access-token",
        "FOO": "bar",
        "BAR": "baz",
    }
    words_to_keep = ["ACCESS_KEY", "ACCESS_TOKEN"]

    result = filter_keys_by_substring(input_dict, words_to_keep)

    assert result == {
        "ACCESS_KEY": "my-access-key",
        "ACCESS_TOKEN": "my-access-token",
    }


def test_mask_sensitive_data_in_file(tmp_path):
    # Create a .env file in the temporary directory
    env_file = tmp_path / ".env"
    env_file.write_text("SECRET_KEY=secret\nPASSWORD=password\nFOO=bar\nBAR=baz")

    # Call mask_sensitive_data with the path to the .env file and a list of sensitive keys
    mask_sensitive_data_in_file(str(env_file), ["SECRET_KEY", "PASSWORD"])

    # Load the .env file and check that the sensitive keys have been masked
    env_vars = dotenv_values(str(env_file))
    assert env_vars["SECRET_KEY"] == "********"  # noqa: S105
    assert env_vars["PASSWORD"] == "********"  # noqa: S105
    assert env_vars["FOO"] == "bar"
    assert env_vars["BAR"] == "baz"
