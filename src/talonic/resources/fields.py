"""Fields resource — list, get, similar. 3 ops."""

from __future__ import annotations

from typing import Any

from talonic._http import AsyncTransport, SyncTransport
from talonic._types.rate_limit import WithRateLimit


def _list_params(
    *,
    search: str | None,
    tier: str | None,
    cluster: str | None,
    limit: int | None,
    cursor: str | None,
) -> dict[str, Any]:
    p: dict[str, Any] = {}
    if search is not None:
        p["search"] = search
    if tier is not None:
        p["tier"] = tier
    if cluster is not None:
        p["cluster"] = cluster
    if limit is not None:
        p["limit"] = limit
    if cursor is not None:
        p["cursor"] = cursor
    return p


class Fields:
    def __init__(self, transport: SyncTransport) -> None:
        self._t = transport

    def list(
        self,
        *,
        search: str | None = None,
        tier: str | None = None,
        cluster: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> WithRateLimit[Any]:
        return self._t.request(
            "GET",
            "/v1/fields",
            params=_list_params(
                search=search, tier=tier, cluster=cluster, limit=limit, cursor=cursor
            ),
        )

    def get(self, field_id: str) -> WithRateLimit[Any]:
        return self._t.request("GET", f"/v1/fields/{field_id}")

    def similar(self, field_id: str, *, limit: int | None = None) -> WithRateLimit[Any]:
        params = {"limit": limit} if limit is not None else None
        return self._t.request("GET", f"/v1/fields/{field_id}/similar", params=params)


class AsyncFields:
    def __init__(self, transport: AsyncTransport) -> None:
        self._t = transport

    async def list(
        self,
        *,
        search: str | None = None,
        tier: str | None = None,
        cluster: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> WithRateLimit[Any]:
        return await self._t.request(
            "GET",
            "/v1/fields",
            params=_list_params(
                search=search, tier=tier, cluster=cluster, limit=limit, cursor=cursor
            ),
        )

    async def get(self, field_id: str) -> WithRateLimit[Any]:
        return await self._t.request("GET", f"/v1/fields/{field_id}")

    async def similar(self, field_id: str, *, limit: int | None = None) -> WithRateLimit[Any]:
        params = {"limit": limit} if limit is not None else None
        return await self._t.request("GET", f"/v1/fields/{field_id}/similar", params=params)
