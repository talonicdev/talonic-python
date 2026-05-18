"""Schemas resource — sync + async parity, all 5 methods."""

import httpx
import respx

from talonic.resources.schemas import AsyncSchemas, Schemas


@respx.mock
def test_schemas_list_sync(sync_transport):
    respx.get("https://api.talonic.com/v1/schemas").mock(
        return_value=httpx.Response(
            200, json={"data": [{"id": "s1", "name": "Invoice"}], "pagination": {"total": 1}}
        )
    )
    r = Schemas(sync_transport).list()
    assert len(r.data["data"]) == 1
    assert r.data["data"][0]["name"] == "Invoice"


@respx.mock
def test_schemas_get_sync(sync_transport):
    respx.get("https://api.talonic.com/v1/schemas/s1").mock(
        return_value=httpx.Response(
            200, json={"id": "s1", "name": "Invoice", "short_id": "SCH-INV"}
        )
    )
    r = Schemas(sync_transport).get("s1")
    assert r.data["id"] == "s1"


@respx.mock
def test_schemas_create_sync(sync_transport):
    route = respx.post("https://api.talonic.com/v1/schemas").mock(
        return_value=httpx.Response(201, json={"id": "s2", "name": "Receipt"})
    )
    r = Schemas(sync_transport).create(name="Receipt", definition={"type": "object"})
    assert r.data["id"] == "s2"
    assert (
        route.calls.last.request.read() == b'{"name": "Receipt", "definition": {"type": "object"}}'
    )


@respx.mock
def test_schemas_update_sync(sync_transport):
    respx.put("https://api.talonic.com/v1/schemas/s2").mock(
        return_value=httpx.Response(200, json={"id": "s2", "name": "Receipt v2"})
    )
    r = Schemas(sync_transport).update("s2", name="Receipt v2")
    assert r.data["name"] == "Receipt v2"


@respx.mock
def test_schemas_delete_sync(sync_transport):
    respx.delete("https://api.talonic.com/v1/schemas/s2").mock(
        return_value=httpx.Response(200, json={"deleted": True})
    )
    r = Schemas(sync_transport).delete("s2")
    assert r.data["deleted"] is True


@respx.mock
async def test_schemas_list_async(async_transport):
    respx.get("https://api.talonic.com/v1/schemas").mock(
        return_value=httpx.Response(200, json={"data": [], "pagination": {"total": 0}})
    )
    r = await AsyncSchemas(async_transport).list()
    assert r.data["data"] == []


@respx.mock
async def test_schemas_create_async(async_transport):
    respx.post("https://api.talonic.com/v1/schemas").mock(
        return_value=httpx.Response(201, json={"id": "s3"})
    )
    r = await AsyncSchemas(async_transport).create(name="X", definition={"type": "object"})
    assert r.data["id"] == "s3"
