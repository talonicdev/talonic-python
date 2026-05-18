"""AsyncTransport.request(): same semantics as SyncTransport."""

import httpx
import pytest
import respx

from talonic._config import TalonicConfig
from talonic._http import AsyncTransport
from talonic.errors import TalonicAuthError, TalonicRateLimitError


@pytest.fixture
async def transport():
    t = AsyncTransport(TalonicConfig(api_key="tlnc_test", max_retries=2))
    yield t
    await t.aclose()


@respx.mock
async def test_async_get_success(transport):
    respx.get("https://api.talonic.com/v1/ping").mock(
        return_value=httpx.Response(200, json={"ok": True})
    )
    result = await transport.request("GET", "/v1/ping")
    assert result.data == {"ok": True}


@respx.mock
async def test_async_401(transport):
    respx.get("https://api.talonic.com/v1/x").mock(
        return_value=httpx.Response(401, json={"code": "AUTH", "message": "bad"})
    )
    with pytest.raises(TalonicAuthError):
        await transport.request("GET", "/v1/x")


@respx.mock
async def test_async_429_retries(transport):
    route = respx.get("https://api.talonic.com/v1/x").mock(
        return_value=httpx.Response(
            429,
            json={"code": "RL", "message": "rl"},
            headers={
                "X-RateLimit-Limit": "1",
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": "1",
            },
        )
    )
    with pytest.raises(TalonicRateLimitError):
        await transport.request("GET", "/v1/x")
    assert route.call_count == 3
