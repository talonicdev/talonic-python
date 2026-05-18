"""Talonic + AsyncTalonic — wiring, top-level extract, top-level search."""

import json

import httpx
import pytest
import respx

from talonic import AsyncTalonic, Talonic
from talonic._types.extract_input import ExtractInputError


def test_construct_with_explicit_key():
    c = Talonic(api_key="tlnc_x")
    assert c.documents is not None
    assert c.extractions is not None
    assert c.fields is not None
    assert c.jobs is not None
    assert c.schemas is not None
    assert c.credits is not None


@respx.mock
def test_extract_file_path_minimal(tmp_path):
    f = tmp_path / "i.pdf"
    f.write_bytes(b"%PDF-1.4\n%%EOF\n")
    route = respx.post("https://api.talonic.com/v1/extract").mock(
        return_value=httpx.Response(
            200, json={"data": {"vendor_name": "Acme"}, "confidence": {"overall": 0.9}}
        )
    )
    c = Talonic(api_key="tlnc_x")
    r = c.extract(
        file_path=str(f),
        schema={"type": "object", "properties": {"vendor_name": {"type": "string"}}},
    )
    assert r.data["data"]["vendor_name"] == "Acme"
    assert route.called


@respx.mock
def test_extract_file_url():
    route = respx.post("https://api.talonic.com/v1/extract").mock(
        return_value=httpx.Response(200, json={"data": {}, "confidence": {"overall": 1.0}})
    )
    Talonic(api_key="tlnc_x").extract(
        file_url="https://example.com/i.pdf",
        schema={"type": "object", "properties": {"x": {"type": "string"}}, "required": ["x"]},
    )
    body = json.loads(route.calls.last.request.read())
    assert body["file_url"] == "https://example.com/i.pdf"


@respx.mock
def test_extract_document_id():
    route = respx.post("https://api.talonic.com/v1/extract").mock(
        return_value=httpx.Response(200, json={"data": {}, "confidence": {"overall": 1.0}})
    )
    Talonic(api_key="tlnc_x").extract(document_id="doc_1", schema_id="sch_1")
    body = json.loads(route.calls.last.request.read())
    assert body == {"document_id": "doc_1", "schema_id": "sch_1"}


def test_extract_requires_schema_or_schema_id():
    with pytest.raises(ExtractInputError, match="schema"):
        Talonic(api_key="tlnc_x").extract(file_url="https://example.com/i.pdf")


def test_extract_auto_populates_required():
    """If properties is supplied but required is missing, fill it from keys."""
    from talonic.client import _normalize_schema  # private helper exercised

    out = _normalize_schema(
        {"type": "object", "properties": {"a": {"type": "string"}, "b": {"type": "number"}}}
    )
    assert out["required"] == ["a", "b"]


def test_extract_two_file_sources_raises():
    with pytest.raises(ExtractInputError, match="exactly one"):
        Talonic(api_key="tlnc_x").extract(
            file_path="/tmp/x",
            file_url="https://x",
            schema={"type": "object", "properties": {"x": {"type": "string"}}},
        )


@respx.mock
def test_search():
    route = respx.get("https://api.talonic.com/v1/search").mock(
        return_value=httpx.Response(
            200,
            json={"documents": [], "fieldMatches": [], "sources": [], "schemas": [], "fields": []},
        )
    )
    Talonic(api_key="tlnc_x").search("invoices", limit=5)
    q = dict(route.calls.last.request.url.params)
    assert q == {"query": "invoices", "limit": "5"}


@respx.mock
async def test_extract_async(tmp_path):
    f = tmp_path / "i.pdf"
    f.write_bytes(b"%PDF-1.4\n%%EOF\n")
    respx.post("https://api.talonic.com/v1/extract").mock(
        return_value=httpx.Response(200, json={"data": {}, "confidence": {"overall": 1}})
    )
    async with AsyncTalonic(api_key="tlnc_x") as c:
        await c.extract(
            file_path=str(f), schema={"type": "object", "properties": {"x": {"type": "string"}}}
        )


@respx.mock
async def test_search_async():
    respx.get("https://api.talonic.com/v1/search").mock(
        return_value=httpx.Response(200, json={"documents": []})
    )
    async with AsyncTalonic(api_key="tlnc_x") as c:
        await c.search("x")
