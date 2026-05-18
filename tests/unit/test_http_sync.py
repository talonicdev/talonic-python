"""SyncTransport.request(): success, retry, error mapping, header parsing."""

import httpx
import pytest
import respx

from talonic._config import TalonicConfig
from talonic._http import SyncTransport
from talonic._types.cost import CostInfo
from talonic._types.rate_limit import RateLimitInfo
from talonic.errors import (
    TalonicAuthError,
    TalonicNotFoundError,
    TalonicRateLimitError,
    TalonicServerError,
)


@pytest.fixture
def transport():
    return SyncTransport(TalonicConfig(api_key="tlnc_test", max_retries=2))


@respx.mock
def test_get_success_parses_rate_limit_and_cost(transport):
    respx.get("https://api.talonic.com/v1/ping").mock(
        return_value=httpx.Response(
            200,
            json={"ok": True},
            headers={
                "X-RateLimit-Limit": "100",
                "X-RateLimit-Remaining": "99",
                "X-RateLimit-Reset": "1700000000",
                "X-Talonic-Cost-Credits": "5",
            },
        )
    )
    result = transport.request("GET", "/v1/ping")
    assert result.data == {"ok": True}
    assert result.rate_limit == RateLimitInfo(100, 99, 1700000000)
    assert isinstance(result.cost, CostInfo)
    assert result.cost.cost_credits == 5


@respx.mock
def test_401_raises_auth_error(transport):
    respx.get("https://api.talonic.com/v1/x").mock(
        return_value=httpx.Response(
            401, json={"code": "AUTH", "message": "bad", "request_id": "rq_1"}
        )
    )
    with pytest.raises(TalonicAuthError) as exc:
        transport.request("GET", "/v1/x")
    assert exc.value.status == 401
    assert exc.value.code == "AUTH"
    assert exc.value.request_id == "rq_1"


@respx.mock
def test_404_raises_not_found(transport):
    respx.get("https://api.talonic.com/v1/x").mock(return_value=httpx.Response(404, json={}))
    with pytest.raises(TalonicNotFoundError):
        transport.request("GET", "/v1/x")


@respx.mock
def test_429_retries_then_raises(transport):
    route = respx.get("https://api.talonic.com/v1/x").mock(
        return_value=httpx.Response(
            429,
            json={"code": "RL", "message": "rate limited"},
            headers={
                "X-RateLimit-Limit": "1",
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": "1700000000",
            },
        )
    )
    with pytest.raises(TalonicRateLimitError) as exc:
        transport.request("GET", "/v1/x")
    assert route.call_count == 3  # 1 initial + 2 retries (max_retries=2)
    assert exc.value.rate_limit is not None
    assert exc.value.rate_limit.limit == 1


@respx.mock
def test_500_retries_then_succeeds(transport):
    route = respx.get("https://api.talonic.com/v1/x").mock(
        side_effect=[
            httpx.Response(500, json={"message": "boom"}),
            httpx.Response(200, json={"ok": True}),
        ]
    )
    result = transport.request("GET", "/v1/x")
    assert result.data == {"ok": True}
    assert route.call_count == 2


@respx.mock
def test_500_retryable_false_skips_retry(transport):
    route = respx.get("https://api.talonic.com/v1/x").mock(
        return_value=httpx.Response(500, json={"message": "fatal", "retryable": False})
    )
    with pytest.raises(TalonicServerError):
        transport.request("GET", "/v1/x")
    assert route.call_count == 1
