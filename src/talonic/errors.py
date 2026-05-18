"""TalonicError hierarchy. One subclass per HTTP failure mode + network/timeout."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from talonic._types.rate_limit import RateLimitInfo


@dataclass
class TalonicError(Exception):
    """Base class for every Talonic SDK error.

    Attributes:
        message: Human-readable description.
        status: HTTP status code (0 for network/timeout failures).
        code: Machine-readable error code from the API ("VALIDATION_ERROR", "NOT_FOUND", ...).
        request_id: Request identifier echoed by the API; useful in support tickets.
    """

    message: str
    status: int = 0
    code: str = ""
    request_id: str | None = None

    def __post_init__(self) -> None:
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


@dataclass
class TalonicAuthError(TalonicError):
    """401 / 403."""


@dataclass
class TalonicNotFoundError(TalonicError):
    """404."""


@dataclass
class TalonicValidationError(TalonicError):
    """400 / 409 / 413 / 422 — request was rejected for shape or business-rule reasons."""


@dataclass
class TalonicRateLimitError(TalonicError):
    """429 — rate-limit hit after retries were exhausted.

    Attributes:
        rate_limit: Parsed RateLimitInfo from the 429 response (never None on a real 429).
    """

    rate_limit: RateLimitInfo | None = None


@dataclass
class TalonicServerError(TalonicError):
    """500 / 502 / 503 / 504 — retried, then surfaced."""


@dataclass
class TalonicNetworkError(TalonicError):
    """DNS, TCP, TLS, connection failures."""


@dataclass
class TalonicTimeoutError(TalonicError):
    """Request exceeded the configured timeout."""


def classify_http_error(status: int) -> type[TalonicError]:
    """Pick the right Talonic*Error subclass for an HTTP status code.

    Falls back to TalonicError for unrecognised statuses; the transport layer
    can still surface them with the raw status and message.
    """
    if status in (401, 403):
        return TalonicAuthError
    if status == 404:
        return TalonicNotFoundError
    if status in (400, 409, 413, 422):
        return TalonicValidationError
    if status == 429:
        return TalonicRateLimitError
    if 500 <= status <= 599:
        return TalonicServerError
    return TalonicError
