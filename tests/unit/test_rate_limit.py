"""RateLimitInfo + WithRateLimit[T] generic wrapper."""

import httpx
import pytest

from talonic._types.rate_limit import RateLimitInfo, WithRateLimit, parse_rate_limit


def headers(**kwargs) -> httpx.Headers:
    return httpx.Headers(kwargs)


def test_parse_rate_limit_present():
    h = headers(
        **{
            "X-RateLimit-Limit": "100",
            "X-RateLimit-Remaining": "42",
            "X-RateLimit-Reset": "1700000000",
        }
    )
    rl = parse_rate_limit(h)
    assert rl == RateLimitInfo(limit=100, remaining=42, reset_at=1700000000)


def test_parse_rate_limit_absent_returns_none():
    assert parse_rate_limit(headers()) is None


def test_parse_rate_limit_partial_returns_none():
    """If only some headers are present, treat the value as missing (defensive)."""
    h = headers(**{"X-RateLimit-Limit": "100"})
    assert parse_rate_limit(h) is None


def test_with_rate_limit_wraps_payload():
    rl = RateLimitInfo(limit=10, remaining=9, reset_at=1)
    wrapped = WithRateLimit(data={"k": "v"}, rate_limit=rl, cost=None)
    assert wrapped.data == {"k": "v"}
    assert wrapped.rate_limit is rl
    assert wrapped.cost is None


@pytest.mark.parametrize("bad", [{}, "", "abc"])
def test_parse_rate_limit_garbage_returns_none(bad):
    """Non-integer header values shouldn't crash; treat as missing."""
    if isinstance(bad, dict):
        assert parse_rate_limit(headers()) is None
    else:
        h = headers(
            **{"X-RateLimit-Limit": bad, "X-RateLimit-Remaining": bad, "X-RateLimit-Reset": bad}
        )
        assert parse_rate_limit(h) is None
