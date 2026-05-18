"""CostInfo: parsed from X-Talonic-Cost-* and X-Talonic-Balance-* headers."""

import httpx

from talonic._types.cost import CostInfo, parse_cost


def headers(**kwargs) -> httpx.Headers:
    return httpx.Headers(kwargs)


def test_parse_cost_full_set():
    h = headers(
        **{
            "X-Talonic-Cost-Credits": "12",
            "X-Talonic-Cost-EUR": "0.024",
            "X-Talonic-Balance-Credits": "988",
            "X-Talonic-Cells-Resolved-Registry": "30",
            "X-Talonic-Cells-Resolved-AI": "70",
        }
    )
    c = parse_cost(h)
    assert c == CostInfo(
        cost_credits=12,
        cost_eur=0.024,
        balance_credits=988,
        cells_resolved_registry=30,
        cells_resolved_ai=70,
    )


def test_parse_cost_no_headers_returns_none():
    assert parse_cost(headers()) is None


def test_parse_cost_required_minimum():
    """If at least cost_credits is present, return a CostInfo with other fields possibly None."""
    h = headers(**{"X-Talonic-Cost-Credits": "5"})
    c = parse_cost(h)
    assert c is not None
    assert c.cost_credits == 5
    assert c.cost_eur is None
    assert c.balance_credits is None


def test_parse_cost_garbage_values_treated_as_missing():
    h = headers(**{"X-Talonic-Cost-Credits": "not-a-number"})
    assert parse_cost(h) is None
