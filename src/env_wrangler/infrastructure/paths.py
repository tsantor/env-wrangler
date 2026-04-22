"""Infrastructure helpers for path formatting."""

from pathlib import Path


def home_agnostic_path(path: str) -> str:
    """Replace the home directory in the given path with a tilde."""
    home = Path.home()
    path = Path(path)
    try:
        relative_path = path.relative_to(home)
        return f"~/{relative_path}"
    except ValueError:
        return str(path)
