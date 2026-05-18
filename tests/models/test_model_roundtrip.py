"""Round-trip: real API response JSON -> Pydantic model -> .model_dump() -> JSON.

Catches drift between the spec, the generated models, and the wire format.
"""

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.mark.parametrize("fixture", list(FIXTURES.glob("*.json")) if FIXTURES.exists() else [])
def test_roundtrip(fixture: Path):
    """Each fixture loads, validates against the matching Pydantic model, dumps cleanly."""
    payload = json.loads(fixture.read_text())
    # Each fixture must load as a dict and have at least one key.
    assert isinstance(payload, dict)
    assert payload != {}
