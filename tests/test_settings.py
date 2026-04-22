import importlib.resources as importlib_resources
from pathlib import Path

from env_wrangler.infrastructure.config import copy_resource_file


def test_copy_resource_file(tmp_path):
    # Create a temp data file in the package resources directory
    data_dir = importlib_resources.files("env_wrangler.data")
    test_file = data_dir.joinpath("test.txt")
    # Actually write the file to the package data directory (for test only)
    test_file_path = Path(str(test_file))
    test_file_path.parent.mkdir(parents=True, exist_ok=True)
    test_file_path.write_text("Test content")

    # Call copy_resource_file with the source file name and a destination path
    copy_resource_file("test.txt", str(tmp_path / "dest" / "test.txt"))

    # Check that the destination file exists and has the correct content
    dest_file = tmp_path / "dest" / "test.txt"
    assert dest_file.is_file()
    assert dest_file.read_text() == "Test content"

    test_file_path.unlink()
