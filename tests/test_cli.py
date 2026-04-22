import json

from click.testing import CliRunner

from env_wrangler.cli import cli


def read_env_file(path):
    lines = path.read_text().splitlines()
    return dict(line.split("=", 1) for line in lines if line)


def write_env_file(path, values):
    content = "\n".join(f"{key}={value}" for key, value in values.items())
    path.write_text(content)


def test_extract_path_is_file(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "env_wrangler.cli.config",
        {
            "default": {
                "key_words": ["SECRET", "PASSWORD"],
                "ignore_keys": ["IGNORED_KEY"],
                "envs": [".env", ".django"],
            }
        },
    )
    runner = CliRunner()
    input_file = tmp_path / "not_a_directory"
    input_file.write_text("FOO=bar")

    result = runner.invoke(cli, ["extract", "--path", str(input_file)])

    assert result.exit_code == 0
    assert "Path is a file, not a directory." in result.output


def test_extract_no_secrets_found(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "env_wrangler.cli.config",
        {
            "default": {
                "key_words": ["SECRET", "PASSWORD"],
                "ignore_keys": ["IGNORED_KEY"],
                "envs": [".env", ".django"],
            }
        },
    )
    runner = CliRunner()
    write_env_file(tmp_path / ".env", {"FOO": "bar"})
    write_env_file(tmp_path / ".django", {"BAR": "baz"})

    result = runner.invoke(cli, ["extract", "--path", str(tmp_path)])

    assert result.exit_code == 0
    assert "No secrets found to extract." in result.output
    assert not (tmp_path / "secrets.json").exists()
    assert not (tmp_path / ".secrets").exists()


def test_extract_json_format(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "env_wrangler.cli.config",
        {
            "default": {
                "key_words": ["SECRET", "PASSWORD"],
                "ignore_keys": ["IGNORED_KEY"],
                "envs": [".env", ".django"],
            }
        },
    )
    runner = CliRunner()
    write_env_file(
        tmp_path / ".env",
        {
            "SECRET_KEY": "secret",
            "PASSWORD": "password",
            "FOO": "bar",
            "ALREADY_MASKED": "********",
        },
    )
    write_env_file(tmp_path / ".django", {"OTHER_SECRET": "other-secret"})

    result = runner.invoke(
        cli, ["extract", "--path", str(tmp_path), "--format", "json"]
    )

    assert result.exit_code == 0
    saved = json.loads((tmp_path / "secrets.json").read_text())
    assert saved == {
        "OTHER_SECRET": "other-secret",
        "PASSWORD": "password",
        "SECRET_KEY": "secret",
    }
    assert not (tmp_path / ".secrets").exists()


def test_extract_env_format(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "env_wrangler.cli.config",
        {
            "default": {
                "key_words": ["SECRET", "PASSWORD"],
                "ignore_keys": ["IGNORED_KEY"],
                "envs": [".env", ".django"],
            }
        },
    )
    runner = CliRunner()
    write_env_file(tmp_path / ".env", {"SECRET_KEY": "secret", "FOO": "bar"})
    write_env_file(tmp_path / ".django", {"PASSWORD": "password"})

    result = runner.invoke(cli, ["extract", "--path", str(tmp_path), "--format", "env"])

    assert result.exit_code == 0
    saved = read_env_file(tmp_path / ".secrets")
    assert saved == {"PASSWORD": "password", "SECRET_KEY": "secret"}
    assert not (tmp_path / "secrets.json").exists()


def test_extract_default_format_saves_both_files(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "env_wrangler.cli.config",
        {
            "default": {
                "key_words": ["SECRET", "PASSWORD"],
                "ignore_keys": ["IGNORED_KEY"],
                "envs": [".env", ".django"],
            }
        },
    )
    runner = CliRunner()
    write_env_file(tmp_path / ".env", {"SECRET_KEY": "secret"})
    write_env_file(tmp_path / ".django", {"PASSWORD": "password"})

    result = runner.invoke(cli, ["extract", "--path", str(tmp_path)])

    assert result.exit_code == 0
    assert (tmp_path / "secrets.json").exists()
    assert (tmp_path / ".secrets").exists()


def test_mask_path_is_file(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "env_wrangler.cli.config",
        {
            "default": {
                "key_words": ["SECRET", "PASSWORD"],
                "ignore_keys": ["IGNORED_KEY"],
                "envs": [".env", ".django"],
            }
        },
    )
    runner = CliRunner()
    input_file = tmp_path / "not_a_directory"
    input_file.write_text("FOO=bar")

    result = runner.invoke(cli, ["mask", "--path", str(input_file)])

    assert result.exit_code == 0
    assert "Path is a file, not a directory." in result.output


def test_mask_requires_secrets_file(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "env_wrangler.cli.config",
        {
            "default": {
                "key_words": ["SECRET", "PASSWORD"],
                "ignore_keys": ["IGNORED_KEY"],
                "envs": [".env", ".django"],
            }
        },
    )
    runner = CliRunner()
    write_env_file(tmp_path / ".env", {"SECRET_KEY": "secret", "FOO": "bar"})

    result = runner.invoke(cli, ["mask", "--path", str(tmp_path)])

    assert result.exit_code == 0
    assert "No secrets file(s) found (.secrets or secrets.json)." in result.output
    assert read_env_file(tmp_path / ".env") == {"SECRET_KEY": "secret", "FOO": "bar"}


def test_mask_masks_matching_keys_and_respects_ignore_keys(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "env_wrangler.cli.config",
        {
            "default": {
                "key_words": ["SECRET", "PASSWORD"],
                "ignore_keys": ["IGNORED_KEY"],
                "envs": [".env", ".django"],
            }
        },
    )
    runner = CliRunner()
    write_env_file(tmp_path / ".secrets", {"SECRET_KEY": "secret"})
    write_env_file(
        tmp_path / ".env",
        {
            "SECRET_KEY": "secret",
            "PASSWORD": "password",
            "IGNORED_KEY": "keep-me",
            "FOO": "bar",
        },
    )

    result = runner.invoke(cli, ["mask", "--path", str(tmp_path)])

    assert result.exit_code == 0
    assert "Masked sensitive data in the following envs:" in result.output
    assert read_env_file(tmp_path / ".env") == {
        "SECRET_KEY": "********",
        "PASSWORD": "********",
        "IGNORED_KEY": "keep-me",
        "FOO": "bar",
    }


def test_unmask_path_is_file(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "env_wrangler.cli.config",
        {
            "default": {
                "key_words": ["SECRET", "PASSWORD"],
                "ignore_keys": ["IGNORED_KEY"],
                "envs": [".env", ".django"],
            }
        },
    )
    runner = CliRunner()
    input_file = tmp_path / "not_a_directory"
    input_file.write_text("FOO=bar")

    result = runner.invoke(cli, ["unmask", "--path", str(input_file)])

    assert result.exit_code == 0
    assert "Path is a file, not a directory." in result.output


def test_unmask_requires_secrets_file(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "env_wrangler.cli.config",
        {
            "default": {
                "key_words": ["SECRET", "PASSWORD"],
                "ignore_keys": ["IGNORED_KEY"],
                "envs": [".env", ".django"],
            }
        },
    )
    runner = CliRunner()
    write_env_file(tmp_path / ".env", {"SECRET_KEY": "********"})

    result = runner.invoke(cli, ["unmask", "--path", str(tmp_path)])

    assert result.exit_code == 0
    assert "No secrets file(s) found (.secrets or secrets.json)." in result.output


def test_unmask_uses_secrets_json_when_env_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "env_wrangler.cli.config",
        {
            "default": {
                "key_words": ["SECRET", "PASSWORD"],
                "ignore_keys": ["IGNORED_KEY"],
                "envs": [".env", ".django"],
            }
        },
    )
    runner = CliRunner()
    write_env_file(
        tmp_path / ".env", {"SECRET_KEY": "********", "PASSWORD": "********"}
    )
    (tmp_path / "secrets.json").write_text(
        json.dumps({"SECRET_KEY": "from-json", "PASSWORD": "json-pass"})
    )

    result = runner.invoke(cli, ["unmask", "--path", str(tmp_path)])

    assert result.exit_code == 0
    assert "Unmasked sensitive data in the following envs:" in result.output
    assert read_env_file(tmp_path / ".env") == {
        "SECRET_KEY": "from-json",
        "PASSWORD": "json-pass",
    }


def test_unmask_prefers_secrets_env_over_json(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "env_wrangler.cli.config",
        {
            "default": {
                "key_words": ["SECRET", "PASSWORD"],
                "ignore_keys": ["IGNORED_KEY"],
                "envs": [".env", ".django"],
            }
        },
    )
    runner = CliRunner()
    write_env_file(
        tmp_path / ".env", {"SECRET_KEY": "********", "PASSWORD": "********"}
    )
    write_env_file(
        tmp_path / ".secrets",
        {"SECRET_KEY": "from-env-file", "PASSWORD": "env-pass"},
    )
    (tmp_path / "secrets.json").write_text(
        json.dumps({"SECRET_KEY": "from-json", "PASSWORD": "json-pass"})
    )

    result = runner.invoke(cli, ["unmask", "--path", str(tmp_path)])

    assert result.exit_code == 0
    assert read_env_file(tmp_path / ".env") == {
        "SECRET_KEY": "from-env-file",
        "PASSWORD": "env-pass",
    }


def test_extract_help_does_not_show_verbose_option():
    runner = CliRunner()
    result = runner.invoke(cli, ["extract", "--help"])

    assert result.exit_code == 0
    assert "--verbose" not in result.output


def test_mask_help_does_not_show_verbose_option():
    runner = CliRunner()
    result = runner.invoke(cli, ["mask", "--help"])

    assert result.exit_code == 0
    assert "--verbose" not in result.output


def test_unmask_help_does_not_show_verbose_option():
    runner = CliRunner()
    result = runner.invoke(cli, ["unmask", "--help"])

    assert result.exit_code == 0
    assert "--verbose" not in result.output
