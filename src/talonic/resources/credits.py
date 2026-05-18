"""Credits resource — get_balance. 1 op."""

from __future__ import annotations

from typing import Any

from talonic._http import AsyncTransport, SyncTransport
from talonic._types.rate_limit import WithRateLimit


class Credits:
    def __init__(self, transport: SyncTransport) -> None:
        self._t = transport

    def get_balance(self) -> WithRateLimit[Any]:
        return self._t.request("GET", "/v1/credits/balance")


class AsyncCredits:
    def __init__(self, transport: AsyncTransport) -> None:
        self._t = transport

    async def get_balance(self) -> WithRateLimit[Any]:
        return await self._t.request("GET", "/v1/credits/balance")
