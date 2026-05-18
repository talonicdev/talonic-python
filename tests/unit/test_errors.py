"""TalonicError hierarchy: subclassing, attributes, classify_from_status."""

import pytest

from talonic.errors import (
    TalonicAuthError,
    TalonicError,
    TalonicNetworkError,
    TalonicNotFoundError,
    TalonicRateLimitError,
    TalonicServerError,
    TalonicTimeoutError,
    TalonicValidationError,
    classify_http_error,
)


def test_base_error_has_required_fields() -> None:
    err = TalonicError(message="boom", status=500, code="X", request_id="rq_1")
    assert err.message == "boom"
    assert err.status == 500
    assert err.code == "X"
    assert err.request_id == "rq_1"
    assert str(err) == "boom"


def test_all_subclasses_inherit_from_base() -> None:
    for cls in (
        TalonicAuthError,
        TalonicNotFoundError,
        TalonicValidationError,
        TalonicRateLimitError,
        TalonicServerError,
        TalonicNetworkError,
        TalonicTimeoutError,
    ):
        assert issubclass(cls, TalonicError)


@pytest.mark.parametrize(
    "status, expected",
    [
        (401, TalonicAuthError),
        (403, TalonicAuthError),
        (404, TalonicNotFoundError),
        (400, TalonicValidationError),
        (409, TalonicValidationError),
        (413, TalonicValidationError),
        (422, TalonicValidationError),
        (429, TalonicRateLimitError),
        (500, TalonicServerError),
        (502, TalonicServerError),
        (503, TalonicServerError),
        (504, TalonicServerError),
    ],
)
def test_classify_http_error(status: int, expected: type[TalonicError]) -> None:
    cls = classify_http_error(status)
    assert cls is expected


def test_classify_unknown_status_returns_base() -> None:
    assert classify_http_error(418) is TalonicError


def test_rate_limit_error_carries_rate_limit_field() -> None:
    from talonic._types.rate_limit import RateLimitInfo  # forward dep — added in Task 6

    rl = RateLimitInfo(limit=100, remaining=0, reset_at=0)
    err = TalonicRateLimitError(message="rl", status=429, code="RL", rate_limit=rl)
    assert err.rate_limit is rl
