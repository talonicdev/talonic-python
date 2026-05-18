"""Smoke tests: package import + version visible."""

from talonic import __version__


def test_import():
    """Importing the package surfaces __version__."""
    assert isinstance(__version__, str)
    assert __version__ != ""


def test_version_matches_pyproject():
    """_version.py is the single source of truth that [tool.hatch.version] reads."""
    import re
    from pathlib import Path

    import tomllib

    repo_root = Path(__file__).parent.parent
    pyproject = tomllib.loads((repo_root / "pyproject.toml").read_text())
    version_path = pyproject["tool"]["hatch"]["version"]["path"]
    assert version_path == "src/talonic/_version.py"

    file_contents = (repo_root / version_path).read_text()
    match = re.search(r'__version__\s*=\s*["\'](.+?)["\']', file_contents)
    assert match is not None, "_version.py must define __version__"
    assert __version__ == match.group(1)
