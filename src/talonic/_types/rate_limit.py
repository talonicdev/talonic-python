"""RateLimitInfo: parsed from X-RateLimit-* headers; WithRateLimit[T]: generic wrapper."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

import httpx

from talonic._types.cost import CostInfo

T = TypeVar("T")


@dataclass(frozen=True)
class RateLimitInfo:
    """Parsed X-RateLimit-* response headers.

    Attributes:
        limit:      Bucket size (e.g. 100 requests).
        remaining:  Requests left in the current window.
        reset_at:   Unix epoch seconds when the bucket resets.
    """

    limit: int
    remaining: int
    reset_at: int


@dataclass
class WithRateLimit(Generic[T]):
    """Generic wrapper returned by every successful SDK call.

    Attributes:
        data:        The endpoint's payload (e.g. DocumentList, Extraction, ...).
        rate_limit:  Parsed X-RateLimit-* info, or None when the response
                     carried no rate-limit headers.
        cost:        Parsed X-Talonic-Cost-* info, or None on read endpoints.
    """

    data: T
    rate_limit: RateLimitInfo | None
    cost: CostInfo | None


def parse_rate_limit(headers: httpx.Headers) -> RateLimitInfo | None:
    """Return a RateLimitInfo when all three X-RateLimit-* headers are present, else None.

    Conservative on purpose: a sentinel "all-zero" or "partial" value silently
    conflated "no limit configured" with "limit hit" in the Node SDK before
    0.1.8; returning None keeps that ambiguity out of the type.
    """
    try:
        limit = int(headers["X-RateLimit-Limit"])
        remaining = int(headers["X-RateLimit-Remaining"])
        reset_at = int(headers["X-RateLimit-Reset"])
    except (KeyError, ValueError):
        return None
    return RateLimitInfo(limit=limit, remaining=remaining, reset_at=reset_at)
