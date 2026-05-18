"""Schemas resource — list, get, create, update, delete. 5 ops."""

from __future__ import annotations

from typing import Any

from talonic._http import AsyncTransport, SyncTransport
from talonic._types.rate_limit import WithRateLimit


class Schemas:
    """Sync access to /v1/schemas."""

    def __init__(self, transport: SyncTransport) -> None:
        self._t = transport

    def list(self) -> WithRateLimit[Any]:
        return self._t.request("GET", "/v1/schemas")

    def get(self, schema_id: str) -> WithRateLimit[Any]:
        return self._t.request("GET", f"/v1/schemas/{schema_id}")

    def create(
        self,
        *,
        name: str,
        definition: dict[str, Any],
        description: str | None = None,
    ) -> WithRateLimit[Any]:
        body: dict[str, Any] = {"name": name, "definition": definition}
        if description is not None:
            body["description"] = description
        return self._t.request("POST", "/v1/schemas", json=body)

    def update(
        self,
        schema_id: str,
        *,
        name: str | None = None,
        definition: dict[str, Any] | None = None,
        description: str | None = None,
    ) -> WithRateLimit[Any]:
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if definition is not None:
            body["definition"] = definition
        if description is not None:
            body["description"] = description
        return self._t.request("PUT", f"/v1/schemas/{schema_id}", json=body)

    def delete(self, schema_id: str) -> WithRateLimit[Any]:
        return self._t.request("DELETE", f"/v1/schemas/{schema_id}")


class AsyncSchemas:
    """Async access to /v1/schemas — identical method names + signatures."""

    def __init__(self, transport: AsyncTransport) -> None:
        self._t = transport

    async def list(self) -> WithRateLimit[Any]:
        return await self._t.request("GET", "/v1/schemas")

    async def get(self, schema_id: str) -> WithRateLimit[Any]:
        return await self._t.request("GET", f"/v1/schemas/{schema_id}")

    async def create(
        self,
        *,
        name: str,
        definition: dict[str, Any],
        description: str | None = None,
    ) -> WithRateLimit[Any]:
        body: dict[str, Any] = {"name": name, "definition": definition}
        if description is not None:
            body["description"] = description
        return await self._t.request("POST", "/v1/schemas", json=body)

    async def update(
        self,
        schema_id: str,
        *,
        name: str | None = None,
        definition: dict[str, Any] | None = None,
        description: str | None = None,
    ) -> WithRateLimit[Any]:
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if definition is not None:
            body["definition"] = definition
        if description is not None:
            body["description"] = description
        return await self._t.request("PUT", f"/v1/schemas/{schema_id}", json=body)

    async def delete(self, schema_id: str) -> WithRateLimit[Any]:
        return await self._t.request("DELETE", f"/v1/schemas/{schema_id}")
