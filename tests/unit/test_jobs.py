"""Jobs resource — create, list, get, get_results, cancel. 5 ops."""

import httpx
import respx

from talonic.resources.jobs import AsyncJobs, Jobs


@respx.mock
def test_create(sync_transport):
    route = respx.post("https://api.talonic.com/v1/jobs").mock(
        return_value=httpx.Response(201, json={"id": "j1", "status": "queued"})
    )
    Jobs(sync_transport).create(schema_id="s1", document_ids=["d1", "d2"])
    body = route.calls.last.request.read()
    assert b'"schema_id": "s1"' in body
    assert b'"document_ids": ["d1", "d2"]' in body


@respx.mock
def test_list(sync_transport):
    respx.get("https://api.talonic.com/v1/jobs").mock(
        return_value=httpx.Response(200, json={"data": []})
    )
    Jobs(sync_transport).list()


@respx.mock
def test_get(sync_transport):
    respx.get("https://api.talonic.com/v1/jobs/j1").mock(
        return_value=httpx.Response(200, json={"id": "j1"})
    )
    Jobs(sync_transport).get("j1")


@respx.mock
def test_get_results(sync_transport):
    respx.get("https://api.talonic.com/v1/jobs/j1/results").mock(
        return_value=httpx.Response(200, json={"data": [{"document_id": "d1", "result": {}}]})
    )
    Jobs(sync_transport).get_results("j1")


@respx.mock
def test_cancel(sync_transport):
    respx.post("https://api.talonic.com/v1/jobs/j1/cancel").mock(
        return_value=httpx.Response(200, json={"id": "j1", "status": "cancelled"})
    )
    Jobs(sync_transport).cancel("j1")


@respx.mock
async def test_create_async(async_transport):
    respx.post("https://api.talonic.com/v1/jobs").mock(
        return_value=httpx.Response(201, json={"id": "j2"})
    )
    await AsyncJobs(async_transport).create(schema_id="s1", document_ids=["d1"])
