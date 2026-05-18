"""Documents resource — list, get, get_markdown, re_extract, delete, filter. 6 ops."""

from __future__ import annotations

import builtins
from typing import Any

from talonic._http import AsyncTransport, SyncTransport
from talonic._types.rate_limit import WithRateLimit


def _list_params(
    *,
    limit: int | None,
    cursor: str | None,
    status: str | None,
    source_id: str | None,
    search: str | None,
    after: str | None,
    before: str | None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if limit is not None:
        params["limit"] = limit
    if cursor is not None:
        params["cursor"] = cursor
    if status is not None:
        params["status"] = status
    if source_id is not None:
        params["source_id"] = source_id
    if search is not None:
        params["search"] = search
    if after is not None:
        params["after"] = after
    if before is not None:
        params["before"] = before
    return params


def _filter_body(
    *,
    conditions: list[dict[str, Any]],
    sort: dict[str, Any] | None,
    search: str | None,
    limit: int | None,
    cursor: str | None,
    source_connection_id: str | None,
) -> dict[str, Any]:
    body: dict[str, Any] = {"conditions": conditions}
    if sort is not None:
        body["sort"] = sort
    if search is not None:
        body["search"] = search
    if limit is not None:
        body["limit"] = limit
    if cursor is not None:
        body["cursor"] = cursor
    if source_connection_id is not None:
        body["source_connection_id"] = source_connection_id
    return body


class Documents:
    def __init__(self, transport: SyncTransport) -> None:
        self._t = transport

    def list(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        status: str | None = None,
        source_id: str | None = None,
        search: str | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> WithRateLimit[Any]:
        return self._t.request(
            "GET",
            "/v1/documents",
            params=_list_params(
                limit=limit,
                cursor=cursor,
                status=status,
                source_id=source_id,
                search=search,
                after=after,
                before=before,
            ),
        )

    def get(self, document_id: str) -> WithRateLimit[Any]:
        return self._t.request("GET", f"/v1/documents/{document_id}")

    def get_markdown(self, document_id: str) -> WithRateLimit[Any]:
        return self._t.request("GET", f"/v1/documents/{document_id}/markdown")

    def re_extract(
        self,
        document_id: str,
        *,
        schema: dict[str, Any] | None = None,
        schema_id: str | None = None,
    ) -> WithRateLimit[Any]:
        body: dict[str, Any] = {}
        if schema is not None:
            body["schema"] = schema
        if schema_id is not None:
            body["schema_id"] = schema_id
        return self._t.request("POST", f"/v1/documents/{document_id}/re-extract", json=body)

    def delete(self, document_id: str) -> WithRateLimit[Any]:
        return self._t.request("DELETE", f"/v1/documents/{document_id}")

    def filter(
        self,
        *,
        conditions: builtins.list[dict[str, Any]],
        sort: dict[str, Any] | None = None,
        search: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        source_connection_id: str | None = None,
    ) -> WithRateLimit[Any]:
        return self._t.request(
            "POST",
            "/v1/documents/filter",
            json=_filter_body(
                conditions=conditions,
                sort=sort,
                search=search,
                limit=limit,
                cursor=cursor,
                source_connection_id=source_connection_id,
            ),
        )


class AsyncDocuments:
    def __init__(self, transport: AsyncTransport) -> None:
        self._t = transport

    async def list(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        status: str | None = None,
        source_id: str | None = None,
        search: str | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> WithRateLimit[Any]:
        return await self._t.request(
            "GET",
            "/v1/documents",
            params=_list_params(
                limit=limit,
                cursor=cursor,
                status=status,
                source_id=source_id,
                search=search,
                after=after,
                before=before,
            ),
        )

    async def get(self, document_id: str) -> WithRateLimit[Any]:
        return await self._t.request("GET", f"/v1/documents/{document_id}")

    async def get_markdown(self, document_id: str) -> WithRateLimit[Any]:
        return await self._t.request("GET", f"/v1/documents/{document_id}/markdown")

    async def re_extract(
        self,
        document_id: str,
        *,
        schema: dict[str, Any] | None = None,
        schema_id: str | None = None,
    ) -> WithRateLimit[Any]:
        body: dict[str, Any] = {}
        if schema is not None:
            body["schema"] = schema
        if schema_id is not None:
            body["schema_id"] = schema_id
        return await self._t.request("POST", f"/v1/documents/{document_id}/re-extract", json=body)

    async def delete(self, document_id: str) -> WithRateLimit[Any]:
        return await self._t.request("DELETE", f"/v1/documents/{document_id}")

    async def filter(
        self,
        *,
        conditions: builtins.list[dict[str, Any]],
        sort: dict[str, Any] | None = None,
        search: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        source_connection_id: str | None = None,
    ) -> WithRateLimit[Any]:
        return await self._t.request(
            "POST",
            "/v1/documents/filter",
            json=_filter_body(
                conditions=conditions,
                sort=sort,
                search=search,
                limit=limit,
                cursor=cursor,
                source_connection_id=source_connection_id,
            ),
        )
