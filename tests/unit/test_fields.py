"""Fields resource — list, get, similar. 3 ops."""

import httpx
import respx

from talonic.resources.fields import AsyncFields, Fields


@respx.mock
def test_list(sync_transport):
    route = respx.get("https://api.talonic.com/v1/fields").mock(
        return_value=httpx.Response(200, json={"data": [{"id": "f1"}]})
    )
    Fields(sync_transport).list(search="vendor", tier="t1", limit=50)
    q = dict(route.calls.last.request.url.params)
    assert q == {"search": "vendor", "tier": "t1", "limit": "50"}


@respx.mock
def test_get(sync_transport):
    respx.get("https://api.talonic.com/v1/fields/f1").mock(
        return_value=httpx.Response(200, json={"id": "f1"})
    )
    Fields(sync_transport).get("f1")


@respx.mock
def test_similar(sync_transport):
    respx.get("https://api.talonic.com/v1/fields/f1/similar").mock(
        return_value=httpx.Response(200, json={"data": [{"id": "f2"}]})
    )
    Fields(sync_transport).similar("f1", limit=10)


@respx.mock
async def test_list_async(async_transport):
    respx.get("https://api.talonic.com/v1/fields").mock(
        return_value=httpx.Response(200, json={"data": []})
    )
    await AsyncFields(async_transport).list()
