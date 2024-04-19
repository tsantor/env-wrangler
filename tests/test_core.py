import json
from pathlib import Path

from dotenv import dotenv_values
from env_wrangler.constants import MASK_VALUE
from env_wrangler.core import envs_to_dict
from env_wrangler.core import filter_keys_by_substring
from env_wrangler.core import json_to_env
from env_wrangler.core import mask_sensitive_data_in_file
from env_wrangler.core import remove_masked_values
from env_wrangler.core import save_dict_to_env_file
from env_wrangler.core import save_dict_to_json_file
from env_wrangler.core import unmask_sensitive_data_in_file


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
    file_path.write_text(json.dumps(data, sort_keys=True))
    output_file = save_dict_to_json_file(data, str(file_path))

    file_path = Path(file_path)
    loaded_data = json.loads(file_path.read_text())

    assert isinstance(output_file, Path)
    assert loaded_data == data


def test_save_empty_dict_to_json_file(tmp_path):
    data = {}
    file_path = tmp_path / "test.json"
    output_file = save_dict_to_json_file(data, str(file_path))

    assert output_file is None


def test_save_dict_to_env_file(tmp_path):
    data = {
        "key1": "value1",
        "key2": "value2",
        "key3": "value3",
        "key4": "value4",
        "key5": "value==5",  # Test bug fix
    }
    file_path = tmp_path / "test.env"
    # Write only a few keys to the file to test that the function appends new keys
    file_path.write_text("key1=value1\nkey2=value2")
    output_file = save_dict_to_env_file(data, str(file_path))

    file_path = Path(file_path)
    lines = file_path.read_text().splitlines()

    loaded_data = {}
    for line in lines:
        key, value = line.split("=", 1)
        loaded_data[key] = value

    assert isinstance(output_file, Path)
    assert loaded_data == data


def test_save_empty_dict_to_env_file(tmp_path):
    data = {}
    file_path = tmp_path / "test.env"
    output_file = save_dict_to_env_file(data, str(file_path))

    assert output_file is None


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


def test_remove_masked_values():
    input_dict = {
        "key1": "value1",
        "key2": MASK_VALUE,
        "key3": "value3",
        "key4": MASK_VALUE,
    }
    expected_dict = {"key1": "value1", "key3": "value3"}

    assert remove_masked_values(input_dict) == expected_dict


def test_mask_sensitive_data_in_file(tmp_path):
    # Create a .env file in the temporary directory
    env_file = tmp_path / ".env"
    env_file.write_text(
        "SECRET_KEY=secret\nPASSWORD=password\nFOO=bar\nBAR=baz\nIGNORED_KEY=ignored"
    )

    # Call mask_sensitive_data with the path to the .env file and a list of sensitive keys
    output_file = mask_sensitive_data_in_file(
        str(env_file), ["KEY", "PASSWORD"], ["IGNORED_KEY"]
    )

    # Load the .env file and check that the sensitive keys have been masked
    env_vars = dotenv_values(str(env_file))
    assert isinstance(output_file, Path)
    assert env_vars["SECRET_KEY"] == MASK_VALUE  # noqa: S105
    assert env_vars["PASSWORD"] == MASK_VALUE  # noqa: S105
    assert env_vars["FOO"] == "bar"
    assert env_vars["BAR"] == "baz"
    assert env_vars["IGNORED_KEY"] == "ignored"


def test_unmask_sensitive_data_in_file(tmp_path):
    # Create a .env file in the temporary directory with masked sensitive data
    env_file = tmp_path / ".env"
    env_file.write_text(
        f"SECRET_KEY={MASK_VALUE}\nPASSWORD={MASK_VALUE}\nFOO=bar\nBAR=baz"
    )

    # Call unmask_sensitive_data_in_file with the path to the .env file, a list of sensitive keys, and their original values
    output_file = unmask_sensitive_data_in_file(
        str(env_file), {"SECRET_KEY": "secret", "PASSWORD": "password"}
    )

    # Load the .env file and check that the sensitive keys have been unmasked
    env_vars = dotenv_values(str(env_file))
    assert isinstance(output_file, Path)
    assert env_vars["SECRET_KEY"] == "secret"  # noqa: S105
    assert env_vars["PASSWORD"] == "password"  # noqa: S105
    assert env_vars["FOO"] == "bar"
    assert env_vars["BAR"] == "baz"


def test_json_to_env(tmp_path):
    # Create a JSON file in the temporary directory
    json_file = tmp_path / "data.json"
    data = {"SECRET_KEY": "secret", "PASSWORD": "password", "FOO": "bar", "BAR": "baz"}
    json_file.write_text(json.dumps(data))

    # Create a path for the .env file
    env_file = tmp_path / ".env"

    # Call json_to_env with the paths to the JSON and .env files
    output_file = json_to_env(str(json_file), str(env_file))

    # Load the .env file and check that it contains the correct data
    env_lines = env_file.read_text().splitlines()
    env_data = dict(line.split("=", 1) for line in env_lines)

    assert isinstance(output_file, Path)
    assert env_data == data
