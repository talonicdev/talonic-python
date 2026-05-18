"""Shared fixtures.

The `transport` fixture is parametrized over ["sync", "async"]; resource
tests can declare `transport` and write a single test that runs against
both flavors. Each test parametrizes the appropriate `client` fixture
defined alongside the resource (e.g. tests/unit/test_documents.py).
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator

import pytest

from talonic._config import TalonicConfig
from talonic._http import AsyncTransport, SyncTransport


@pytest.fixture
def config() -> TalonicConfig:
    return TalonicConfig(api_key="tlnc_test", max_retries=0)


@pytest.fixture
def sync_transport(config) -> Iterator[SyncTransport]:
    t = SyncTransport(config)
    yield t
    t.close()


@pytest.fixture
async def async_transport(config) -> AsyncIterator[AsyncTransport]:
    t = AsyncTransport(config)
    yield t
    await t.aclose()


def pytest_addoption(parser):
    parser.addoption(
        "--live",
        action="store_true",
        default=False,
        help="Run tests marked `live` against api.talonic.com",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--live"):
        return
    skip_live = pytest.mark.skip(reason="needs --live to run against production")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)
