"""Extractions resource — list, get, get_data (dict & csv), patch. 4 ops."""

import httpx
import respx

from talonic.resources.extractions import AsyncExtractions, Extractions


@respx.mock
def test_list(sync_transport):
    respx.get("https://api.talonic.com/v1/extractions").mock(
        return_value=httpx.Response(200, json={"data": []})
    )
    Extractions(sync_transport).list(document_id="d1")


@respx.mock
def test_get(sync_transport):
    respx.get("https://api.talonic.com/v1/extractions/e1").mock(
        return_value=httpx.Response(200, json={"id": "e1"})
    )
    Extractions(sync_transport).get("e1")


@respx.mock
def test_get_data_json(sync_transport):
    respx.get("https://api.talonic.com/v1/extractions/e1/data").mock(
        return_value=httpx.Response(200, json={"vendor_name": "Acme"})
    )
    r = Extractions(sync_transport).get_data("e1")
    assert r.data == {"vendor_name": "Acme"}


@respx.mock
def test_get_data_csv(sync_transport):
    respx.get("https://api.talonic.com/v1/extractions/e1/data").mock(
        return_value=httpx.Response(
            200, text="vendor_name\nAcme\n", headers={"content-type": "text/csv"}
        )
    )
    csv = Extractions(sync_transport).get_data("e1", format="csv")
    assert csv.startswith("vendor_name")


@respx.mock
def test_patch(sync_transport):
    route = respx.patch("https://api.talonic.com/v1/extractions/e1/data").mock(
        return_value=httpx.Response(200, json={"updated": True})
    )
    Extractions(sync_transport).patch(
        "e1", corrections=[{"path": "vendor_name", "value": "Acme Corp"}]
    )
    body = route.calls.last.request.read()
    assert b"corrections" in body


@respx.mock
async def test_get_data_async(async_transport):
    respx.get("https://api.talonic.com/v1/extractions/e1/data").mock(
        return_value=httpx.Response(200, json={})
    )
    await AsyncExtractions(async_transport).get_data("e1")
