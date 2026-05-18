"""HTTP transport for the Talonic SDK.

BaseTransport holds pure, side-effect-free helpers shared between
SyncTransport (Task 11) and AsyncTransport (Task 12): header building,
retry-decision logic, exponential backoff with jitter, header parsing.
"""

from __future__ import annotations

import contextlib
import random
import time
from json import JSONDecodeError
from typing import Any, cast

import httpx

from talonic._config import TalonicConfig
from talonic._types.cost import parse_cost
from talonic._types.rate_limit import WithRateLimit, parse_rate_limit
from talonic._version import __version__
from talonic.errors import (
    TalonicError,
    TalonicNetworkError,
    TalonicRateLimitError,
    TalonicTimeoutError,
    classify_http_error,
)

_USER_AGENT = f"talonic-python/{__version__} httpx/{httpx.__version__}"
_BACKOFF_CAP_SECONDS = 16.0
_BACKOFF_BASE_SECONDS = 0.5


class BaseTransport:
    """Pure helpers shared between sync + async transports.

    Subclasses provide the actual `request()` method that does I/O.
    """

    def __init__(self, config: TalonicConfig) -> None:
        self._config = config

    def _build_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._config.api_key}",
            "User-Agent": _USER_AGENT,
            "Accept": "application/json",
        }

    def _should_retry_status(self, status: int, body: dict[str, Any] | None) -> bool:
        """Status alone says retryable; but the API can opt out with `retryable: false`."""
        if body is not None and body.get("retryable") is False:
            return False
        return status == 429 or 500 <= status <= 504

    def _should_retry_attempt(self, attempt: int) -> bool:
        """Attempt 0 is the first request; we retry up to max_retries times."""
        return attempt < self._config.max_retries

    def _backoff_delay(self, attempt: int) -> float:
        """Exponential backoff with full jitter, capped at _BACKOFF_CAP_SECONDS."""
        ceiling = min(_BACKOFF_BASE_SECONDS * (2**attempt), _BACKOFF_CAP_SECONDS)
        return random.uniform(0, ceiling)

    def _retry_after_seconds(self, headers: httpx.Headers) -> float | None:
        """Parse `Retry-After` header as seconds.

        Integer form only; HTTP-date parsing not implemented in v0.1.
        """
        raw = headers.get("Retry-After")
        if raw is None:
            return None
        try:
            return float(raw)
        except ValueError:
            return None


def _build_error(response: httpx.Response) -> TalonicError:
    """Map an HTTP response to the right TalonicError subclass."""
    body: dict[str, Any] = {}
    with contextlib.suppress(JSONDecodeError):
        body = response.json()
    cls = classify_http_error(response.status_code)
    rate_limit = parse_rate_limit(response.headers)
    kwargs: dict[str, Any] = {
        "message": body.get("message", response.text or response.reason_phrase or "request failed"),
        "status": response.status_code,
        "code": body.get("code", ""),
        "request_id": body.get("request_id"),
    }
    if cls is TalonicRateLimitError:
        kwargs["rate_limit"] = rate_limit
    return cls(**kwargs)


class SyncTransport(BaseTransport):
    """Sync HTTP transport built on httpx.Client."""

    def __init__(self, config: TalonicConfig) -> None:
        super().__init__(config)
        self._client = httpx.Client(
            base_url=config.base_url or "",
            timeout=config.timeout,
            headers=self._build_headers(),
            transport=config.transport,
        )

    def __enter__(self) -> SyncTransport:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> WithRateLimit[Any]:
        json_body = json  # avoid shadowing the `json` stdlib module below
        attempt = 0
        last_exc: TalonicError | None = None
        while True:
            try:
                response = self._client.request(
                    method, path, params=params, json=json_body, files=files, data=data
                )
            except httpx.TimeoutException as exc:
                last_exc = TalonicTimeoutError(message=str(exc), code="TIMEOUT")
            except httpx.NetworkError as exc:
                last_exc = TalonicNetworkError(message=str(exc), code="NETWORK")
            else:
                if response.status_code < 400:
                    body = response.json() if response.content else {}
                    return WithRateLimit(
                        data=body,
                        rate_limit=parse_rate_limit(response.headers),
                        cost=parse_cost(response.headers),
                    )
                body = {}
                with contextlib.suppress(JSONDecodeError):
                    body = response.json()
                if self._should_retry_status(
                    response.status_code, body
                ) and self._should_retry_attempt(attempt):
                    delay = self._retry_after_seconds(response.headers) or self._backoff_delay(
                        attempt
                    )
                    time.sleep(delay)
                    attempt += 1
                    continue
                raise _build_error(response)

            # Network/timeout fall-through:
            if self._should_retry_attempt(attempt):
                time.sleep(self._backoff_delay(attempt))
                attempt += 1
                continue
            raise cast(TalonicError, last_exc)
