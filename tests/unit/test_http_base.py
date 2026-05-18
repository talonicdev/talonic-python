"""BaseTransport pure helpers: headers, retry decision, backoff."""

import httpx
import pytest

from talonic._config import TalonicConfig
from talonic._http import BaseTransport


@pytest.fixture
def base():
    return BaseTransport(TalonicConfig(api_key="tlnc_test"))


def test_build_headers_includes_auth_and_user_agent(base):
    h = base._build_headers()
    assert h["Authorization"] == "Bearer tlnc_test"
    assert h["User-Agent"].startswith("talonic-python/")
    assert h["Accept"] == "application/json"


@pytest.mark.parametrize(
    "status, retryable, expected",
    [
        (200, None, False),
        (400, None, False),
        (401, None, False),
        (404, None, False),
        (429, None, True),
        (500, None, True),
        (502, None, True),
        (503, None, True),
        (504, None, True),
        (500, False, False),  # API explicitly marked non-retryable
    ],
)
def test_should_retry_status_code(base, status, retryable, expected):
    body = None if retryable is None else {"retryable": retryable}
    assert base._should_retry_status(status, body) is expected


def test_should_retry_caps_attempts(base):
    assert base._should_retry_attempt(0) is True
    assert base._should_retry_attempt(2) is True
    assert base._should_retry_attempt(3) is False  # max_retries=3 → 4 total attempts


def test_backoff_delay_grows_exponentially(base):
    d0 = base._backoff_delay(0)
    d1 = base._backoff_delay(1)
    d2 = base._backoff_delay(2)
    # Test the caps rather than relying on random ordering (full jitter means
    # any sample could be smaller than a sample from a lower-cap range).
    assert d0 <= 0.5
    assert d1 <= 1.0
    assert d2 <= 2.0


def test_backoff_delay_respects_retry_after_header(base):
    h = httpx.Headers({"Retry-After": "2"})
    assert base._retry_after_seconds(h) == 2.0


def test_retry_after_missing_returns_none(base):
    assert base._retry_after_seconds(httpx.Headers()) is None
