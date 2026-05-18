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
