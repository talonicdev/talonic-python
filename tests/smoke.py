"""Smoke tests: package import + version visible."""

from talonic import __version__


def test_import():
    """Importing the package surfaces __version__."""
    assert isinstance(__version__, str)
    assert __version__ != ""


def test_version_matches_pyproject():
    """_version.py value should match the [tool.hatch.version] source of truth."""
    from pathlib import Path

    import tomllib

    pyproject = tomllib.loads(Path("pyproject.toml").read_text())
    expected_path = pyproject["tool"]["hatch"]["version"]["path"]
    assert expected_path == "src/talonic/_version.py"
    assert __version__ == "0.1.0"
