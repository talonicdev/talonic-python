"""Jobs resource — create, list, get, get_results, cancel. 5 ops."""

from __future__ import annotations

import builtins
from typing import Any

from talonic._http import AsyncTransport, SyncTransport
from talonic._types.rate_limit import WithRateLimit


def _list_params(*, status: str | None, limit: int | None, cursor: str | None) -> dict[str, Any]:
    p: dict[str, Any] = {}
    if status is not None:
        p["status"] = status
    if limit is not None:
        p["limit"] = limit
    if cursor is not None:
        p["cursor"] = cursor
    return p


def _create_body(
    *,
    schema_id: str,
    document_ids: builtins.list[str],
    include_provenance: bool | None,
) -> dict[str, Any]:
    body: dict[str, Any] = {"schema_id": schema_id, "document_ids": document_ids}
    if include_provenance is not None:
        body["include_provenance"] = include_provenance
    return body


class Jobs:
    def __init__(self, transport: SyncTransport) -> None:
        self._t = transport

    def create(
        self,
        *,
        schema_id: str,
        document_ids: builtins.list[str],
        include_provenance: bool | None = None,
    ) -> WithRateLimit[Any]:
        return self._t.request(
            "POST",
            "/v1/jobs",
            json=_create_body(
                schema_id=schema_id,
                document_ids=document_ids,
                include_provenance=include_provenance,
            ),
        )

    def list(
        self,
        *,
        status: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> WithRateLimit[Any]:
        return self._t.request(
            "GET",
            "/v1/jobs",
            params=_list_params(status=status, limit=limit, cursor=cursor),
        )

    def get(self, job_id: str) -> WithRateLimit[Any]:
        return self._t.request("GET", f"/v1/jobs/{job_id}")

    def get_results(self, job_id: str) -> WithRateLimit[Any]:
        return self._t.request("GET", f"/v1/jobs/{job_id}/results")

    def cancel(self, job_id: str) -> WithRateLimit[Any]:
        return self._t.request("POST", f"/v1/jobs/{job_id}/cancel")


class AsyncJobs:
    def __init__(self, transport: AsyncTransport) -> None:
        self._t = transport

    async def create(
        self,
        *,
        schema_id: str,
        document_ids: builtins.list[str],
        include_provenance: bool | None = None,
    ) -> WithRateLimit[Any]:
        return await self._t.request(
            "POST",
            "/v1/jobs",
            json=_create_body(
                schema_id=schema_id,
                document_ids=document_ids,
                include_provenance=include_provenance,
            ),
        )

    async def list(
        self,
        *,
        status: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> WithRateLimit[Any]:
        return await self._t.request(
            "GET",
            "/v1/jobs",
            params=_list_params(status=status, limit=limit, cursor=cursor),
        )

    async def get(self, job_id: str) -> WithRateLimit[Any]:
        return await self._t.request("GET", f"/v1/jobs/{job_id}")

    async def get_results(self, job_id: str) -> WithRateLimit[Any]:
        return await self._t.request("GET", f"/v1/jobs/{job_id}/results")

    async def cancel(self, job_id: str) -> WithRateLimit[Any]:
        return await self._t.request("POST", f"/v1/jobs/{job_id}/cancel")
