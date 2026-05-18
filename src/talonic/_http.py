"""HTTP transport for the Talonic SDK.

BaseTransport holds pure, side-effect-free helpers shared between
SyncTransport (Task 11) and AsyncTransport (Task 12): header building,
retry-decision logic, exponential backoff with jitter, header parsing.
"""

from __future__ import annotations

import random
from typing import Any

import httpx

from talonic._config import TalonicConfig
from talonic._version import __version__

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
