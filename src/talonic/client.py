"""Talonic + AsyncTalonic — the user-facing entry points.

Wires the SyncTransport / AsyncTransport into the resource classes and
exposes top-level extract() + search() methods.
"""

from __future__ import annotations

import json as _json
import os
from pathlib import Path
from typing import Any

import httpx

from talonic._config import TalonicConfig
from talonic._http import AsyncTransport, SyncTransport
from talonic._types.extract_input import ExtractInputError, normalize_extract_input
from talonic._types.rate_limit import WithRateLimit
from talonic.resources.credits import AsyncCredits, Credits
from talonic.resources.documents import AsyncDocuments, Documents
from talonic.resources.extractions import AsyncExtractions, Extractions
from talonic.resources.fields import AsyncFields, Fields
from talonic.resources.jobs import AsyncJobs, Jobs
from talonic.resources.schemas import AsyncSchemas, Schemas


def _normalize_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """If `properties` is present but `required` is not, fill required with all property keys.

    Mirrors @talonic/node's autoPopulateRequired guardrail.
    """
    if "properties" in schema and "required" not in schema:
        schema = {**schema, "required": list(schema["properties"].keys())}
    return schema


def _build_extract_body_or_multipart(
    *,
    file_path: str | None,
    file_url: str | None,
    file_data: bytes | None,
    filename: str | None,
    document_id: str | None,
    schema: dict[str, Any] | None,
    schema_id: str | None,
    include_markdown: bool,
    include_provenance: bool,
) -> tuple[dict[str, Any], dict[str, tuple[str, bytes, str]] | None, dict[str, Any] | None]:
    """Returns (json_body, files, form_data) appropriate for the chosen file source.

    For file_path / file_data → multipart (files + form_data).
    For file_url / document_id → JSON body only.
    """
    source = normalize_extract_input(
        file_data=file_data,
        filename=filename,
        file_path=file_path,
        file_url=file_url,
        document_id=document_id,
    )
    if schema is None and schema_id is None:
        raise ExtractInputError("extract() requires either a `schema` or `schema_id`.")

    base: dict[str, Any] = {}
    if schema is not None:
        base["schema"] = _normalize_schema(schema)
    if schema_id is not None:
        base["schema_id"] = schema_id
    if include_markdown:
        base["include_markdown"] = True
    if include_provenance:
        base["include_provenance"] = True

    if "file_path" in source:
        path = Path(source["file_path"])
        files = {"file": (path.name, path.read_bytes(), _guess_content_type(path.name))}
        return ({}, files, _serialize_form(base))
    if "file_data" in source:
        files = {
            "file": (
                source["filename"],
                source["file_data"],
                _guess_content_type(source["filename"]),
            )
        }
        return ({}, files, _serialize_form(base))
    # URL / document_id → JSON body only.
    base.update(source)
    return (base, None, None)


def _serialize_form(data: dict[str, Any]) -> dict[str, str]:
    """Convert form-data dict values to strings for httpx multipart.

    httpx requires all data field values to be primitive types (str/bytes/int/float).
    Dicts and lists must be JSON-serialized to strings before passing as `data=`.
    """
    result: dict[str, str] = {}
    for key, value in data.items():
        if isinstance(value, (dict, list)):
            result[key] = _json.dumps(value)
        else:
            result[key] = str(value)
    return result


def _guess_content_type(filename: str) -> str:
    import mimetypes

    return mimetypes.guess_type(filename)[0] or "application/octet-stream"


class Talonic:
    """Sync entry point. Use as a context manager or call close() manually."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 60.0,
        max_retries: int = 3,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._config = TalonicConfig(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            transport=transport,
        )
        self._transport = SyncTransport(self._config)
        self.documents = Documents(self._transport)
        self.extractions = Extractions(self._transport)
        self.fields = Fields(self._transport)
        self.jobs = Jobs(self._transport)
        self.schemas = Schemas(self._transport)
        self.credits = Credits(self._transport)

    def __enter__(self) -> Talonic:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        self._transport.close()

    def extract(
        self,
        *,
        file_path: str | os.PathLike[str] | None = None,
        file_url: str | None = None,
        file_data: bytes | None = None,
        filename: str | None = None,
        document_id: str | None = None,
        schema: dict[str, Any] | None = None,
        schema_id: str | None = None,
        include_markdown: bool = False,
        include_provenance: bool = False,
    ) -> WithRateLimit[Any]:
        body, files, form = _build_extract_body_or_multipart(
            file_path=str(file_path) if file_path is not None else None,
            file_url=file_url,
            file_data=file_data,
            filename=filename,
            document_id=document_id,
            schema=schema,
            schema_id=schema_id,
            include_markdown=include_markdown,
            include_provenance=include_provenance,
        )
        if files is not None:
            return self._transport.request("POST", "/v1/extract", files=files, data=form)
        return self._transport.request("POST", "/v1/extract", json=body)

    def search(self, query: str, *, limit: int | None = None) -> WithRateLimit[Any]:
        params: dict[str, Any] = {"query": query}
        if limit is not None:
            params["limit"] = limit
        return self._transport.request("GET", "/v1/search", params=params)


class AsyncTalonic:
    """Async entry point. Use as an async context manager."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 60.0,
        max_retries: int = 3,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._config = TalonicConfig(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            transport=transport,
        )
        self._transport = AsyncTransport(self._config)
        self.documents = AsyncDocuments(self._transport)
        self.extractions = AsyncExtractions(self._transport)
        self.fields = AsyncFields(self._transport)
        self.jobs = AsyncJobs(self._transport)
        self.schemas = AsyncSchemas(self._transport)
        self.credits = AsyncCredits(self._transport)

    async def __aenter__(self) -> AsyncTalonic:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._transport.aclose()

    async def extract(
        self,
        *,
        file_path: str | os.PathLike[str] | None = None,
        file_url: str | None = None,
        file_data: bytes | None = None,
        filename: str | None = None,
        document_id: str | None = None,
        schema: dict[str, Any] | None = None,
        schema_id: str | None = None,
        include_markdown: bool = False,
        include_provenance: bool = False,
    ) -> WithRateLimit[Any]:
        body, files, form = _build_extract_body_or_multipart(
            file_path=str(file_path) if file_path is not None else None,
            file_url=file_url,
            file_data=file_data,
            filename=filename,
            document_id=document_id,
            schema=schema,
            schema_id=schema_id,
            include_markdown=include_markdown,
            include_provenance=include_provenance,
        )
        if files is not None:
            return await self._transport.request("POST", "/v1/extract", files=files, data=form)
        return await self._transport.request("POST", "/v1/extract", json=body)

    async def search(self, query: str, *, limit: int | None = None) -> WithRateLimit[Any]:
        params: dict[str, Any] = {"query": query}
        if limit is not None:
            params["limit"] = limit
        return await self._transport.request("GET", "/v1/search", params=params)
