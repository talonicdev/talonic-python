"""Live integration tests against api.talonic.com.

Skip by default; require --live flag.
Need TALONIC_API_KEY in env.
"""

import os

import pytest

from talonic import Talonic


@pytest.fixture(scope="module")
def client():
    key = os.environ.get("TALONIC_API_KEY")
    if not key:
        pytest.skip("TALONIC_API_KEY not set")
    with Talonic() as c:
        yield c


pytestmark = pytest.mark.live


def test_credits_balance(client):
    r = client.credits.get_balance()
    assert r.data["balance_credits"] >= 0


def test_search(client):
    r = client.search("invoice", limit=3)
    assert isinstance(r.data["documents"], list)


def test_schemas_list(client):
    r = client.schemas.list()
    assert "data" in r.data


def test_documents_list_first_page(client):
    r = client.documents.list(limit=5)
    assert "data" in r.data
