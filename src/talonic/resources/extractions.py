"""Extractions resource — list, get, get_data (dict or csv), patch. 4 ops.

`get_data` has two return modes:
- default: JSON dict, returned as WithRateLimit[dict[str, Any]]
- format="csv": raw CSV string, returned as str (no rate-limit wrapping; mirrors @talonic/node).
"""

from __future__ import annotations

import builtins
from typing import Any, Literal, overload

from talonic._http import AsyncTransport, SyncTransport
from talonic._types.rate_limit import WithRateLimit


def _list_params(
    *, document_id: str | None, limit: int | None, cursor: str | None
) -> dict[str, Any]:
    p: dict[str, Any] = {}
    if document_id is not None:
        p["document_id"] = document_id
    if limit is not None:
        p["limit"] = limit
    if cursor is not None:
        p["cursor"] = cursor
    return p


class Extractions:
    def __init__(self, transport: SyncTransport) -> None:
        self._t = transport

    def list(
        self,
        *,
        document_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> WithRateLimit[Any]:
        return self._t.request(
            "GET",
            "/v1/extractions",
            params=_list_params(document_id=document_id, limit=limit, cursor=cursor),
        )

    def get(self, extraction_id: str) -> WithRateLimit[Any]:
        return self._t.request("GET", f"/v1/extractions/{extraction_id}")

    @overload
    def get_data(self, extraction_id: str) -> WithRateLimit[dict[str, Any]]: ...
    @overload
    def get_data(self, extraction_id: str, *, format: Literal["csv"]) -> str: ...
    def get_data(
        self, extraction_id: str, *, format: Literal["csv"] | None = None
    ) -> WithRateLimit[Any] | str:
        if format == "csv":
            # Bypass JSON parsing — return the raw response body.
            # NOTE: errors here raise httpx.HTTPStatusError, not TalonicError.
            # This is plan-as-written; resource-level error mapping for the
            # bypass path is a v0.2 improvement.
            r = self._t._client.get(
                f"/v1/extractions/{extraction_id}/data", params={"format": "csv"}
            )
            r.raise_for_status()
            return r.text
        return self._t.request("GET", f"/v1/extractions/{extraction_id}/data")

    def patch(
        self,
        extraction_id: str,
        *,
        corrections: builtins.list[dict[str, Any]],
    ) -> WithRateLimit[Any]:
        return self._t.request(
            "PATCH",
            f"/v1/extractions/{extraction_id}/data",
            json={"corrections": corrections},
        )


class AsyncExtractions:
    def __init__(self, transport: AsyncTransport) -> None:
        self._t = transport

    async def list(
        self,
        *,
        document_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> WithRateLimit[Any]:
        return await self._t.request(
            "GET",
            "/v1/extractions",
            params=_list_params(document_id=document_id, limit=limit, cursor=cursor),
        )

    async def get(self, extraction_id: str) -> WithRateLimit[Any]:
        return await self._t.request("GET", f"/v1/extractions/{extraction_id}")

    @overload
    async def get_data(self, extraction_id: str) -> WithRateLimit[dict[str, Any]]: ...
    @overload
    async def get_data(self, extraction_id: str, *, format: Literal["csv"]) -> str: ...
    async def get_data(
        self, extraction_id: str, *, format: Literal["csv"] | None = None
    ) -> WithRateLimit[Any] | str:
        if format == "csv":
            # Bypass JSON parsing — return the raw response body.
            # NOTE: errors here raise httpx.HTTPStatusError, not TalonicError.
            r = await self._t._client.get(
                f"/v1/extractions/{extraction_id}/data", params={"format": "csv"}
            )
            r.raise_for_status()
            return r.text
        return await self._t.request("GET", f"/v1/extractions/{extraction_id}/data")

    async def patch(
        self,
        extraction_id: str,
        *,
        corrections: builtins.list[dict[str, Any]],
    ) -> WithRateLimit[Any]:
        return await self._t.request(
            "PATCH",
            f"/v1/extractions/{extraction_id}/data",
            json={"corrections": corrections},
        )
