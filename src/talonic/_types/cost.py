"""CostInfo: per-call cost surfaced from X-Talonic-Cost-* response headers."""

from __future__ import annotations

from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class CostInfo:
    """Per-call cost reported by the Talonic API.

    Attributes:
        cost_credits:            Credits debited for this call.
        cost_eur:                EUR equivalent (None when not reported).
        balance_credits:         Credits remaining after this call.
        cells_resolved_registry: Cells answered from the field registry (no AI cost).
        cells_resolved_ai:       Cells answered by AI (consumed credits).
    """

    cost_credits: int
    cost_eur: float | None = None
    balance_credits: int | None = None
    cells_resolved_registry: int | None = None
    cells_resolved_ai: int | None = None


def _int_or_none(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _float_or_none(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_cost(headers: httpx.Headers) -> CostInfo | None:
    """Return a CostInfo when the minimum required header (X-Talonic-Cost-Credits)
    is present and parseable. Otherwise None.
    """
    credits = _int_or_none(headers.get("X-Talonic-Cost-Credits"))
    if credits is None:
        return None
    return CostInfo(
        cost_credits=credits,
        cost_eur=_float_or_none(headers.get("X-Talonic-Cost-EUR")),
        balance_credits=_int_or_none(headers.get("X-Talonic-Balance-Credits")),
        cells_resolved_registry=_int_or_none(headers.get("X-Talonic-Cells-Resolved-Registry")),
        cells_resolved_ai=_int_or_none(headers.get("X-Talonic-Cells-Resolved-AI")),
    )
