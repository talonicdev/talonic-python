"""Documents resource — list, get, get_markdown, re_extract, delete, filter. 6 ops."""

import httpx
import respx

from talonic.resources.documents import AsyncDocuments, Documents


@respx.mock
def test_list_with_params(sync_transport):
    route = respx.get("https://api.talonic.com/v1/documents").mock(
        return_value=httpx.Response(200, json={"data": [], "pagination": {}})
    )
    Documents(sync_transport).list(limit=50, status="completed", search="invoice")
    q = dict(route.calls.last.request.url.params)
    assert q == {"limit": "50", "status": "completed", "search": "invoice"}


@respx.mock
def test_get(sync_transport):
    respx.get("https://api.talonic.com/v1/documents/d1").mock(
        return_value=httpx.Response(200, json={"id": "d1"})
    )
    assert Documents(sync_transport).get("d1").data["id"] == "d1"


@respx.mock
def test_get_markdown(sync_transport):
    respx.get("https://api.talonic.com/v1/documents/d1/markdown").mock(
        return_value=httpx.Response(200, json={"markdown": "# Invoice\n..."})
    )
    assert Documents(sync_transport).get_markdown("d1").data["markdown"].startswith("# Invoice")


@respx.mock
def test_re_extract(sync_transport):
    respx.post("https://api.talonic.com/v1/documents/d1/re-extract").mock(
        return_value=httpx.Response(200, json={"id": "ext_1"})
    )
    assert Documents(sync_transport).re_extract("d1").data["id"] == "ext_1"


@respx.mock
def test_delete(sync_transport):
    respx.delete("https://api.talonic.com/v1/documents/d1").mock(
        return_value=httpx.Response(200, json={"deleted": True})
    )
    assert Documents(sync_transport).delete("d1").data == {"deleted": True}


@respx.mock
def test_filter(sync_transport):
    route = respx.post("https://api.talonic.com/v1/documents/filter").mock(
        return_value=httpx.Response(200, json={"data": [], "pagination": {}})
    )
    Documents(sync_transport).filter(
        conditions=[{"field": "vendor.name", "operator": "is_not_empty"}],
        sort={"field": "created_at", "direction": "desc"},
        limit=20,
    )
    body = route.calls.last.request.read()
    assert b'"conditions"' in body
    assert b'"sort"' in body


@respx.mock
async def test_list_async(async_transport):
    respx.get("https://api.talonic.com/v1/documents").mock(
        return_value=httpx.Response(200, json={"data": []})
    )
    r = await AsyncDocuments(async_transport).list()
    assert r.data == {"data": []}
