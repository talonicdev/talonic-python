"""CLI commands smoke + happy-path + error paths."""

import json

import httpx
import respx
from typer.testing import CliRunner

from talonic.cli import app

# Note: Typer 0.25.1 does not support mix_stderr=False; stdout/stderr are still
# available as separate attributes on the result object without that flag.
runner = CliRunner()


def test_version():
    r = runner.invoke(app, ["--version"])
    assert r.exit_code == 0
    assert r.stdout.strip().startswith("talonic ")


def test_help():
    r = runner.invoke(app, ["--help"])
    assert r.exit_code == 0
    assert "extract" in r.stdout


def test_missing_api_key(monkeypatch):
    monkeypatch.delenv("TALONIC_API_KEY", raising=False)
    r = runner.invoke(app, ["schemas", "list"])
    assert r.exit_code == 1
    assert "TALONIC_API_KEY" in r.stderr


@respx.mock
def test_schemas_list(monkeypatch):
    monkeypatch.setenv("TALONIC_API_KEY", "tlnc_x")
    respx.get("https://api.talonic.com/v1/schemas").mock(
        return_value=httpx.Response(200, json={"data": [{"id": "s1", "name": "Invoice"}]})
    )
    r = runner.invoke(app, ["schemas", "list"])
    assert r.exit_code == 0
    body = json.loads(r.stdout)
    assert body["data"][0]["name"] == "Invoice"


@respx.mock
def test_extract_file_url(monkeypatch):
    monkeypatch.setenv("TALONIC_API_KEY", "tlnc_x")
    respx.post("https://api.talonic.com/v1/extract").mock(
        return_value=httpx.Response(200, json={"data": {"x": 1}, "confidence": {"overall": 1.0}})
    )
    r = runner.invoke(
        app,
        [
            "extract",
            "--file-url",
            "https://example.com/i.pdf",
            "--schema",
            '{"type":"object","properties":{"x":{"type":"number"}},"required":["x"]}',
        ],
    )
    assert r.exit_code == 0
    assert '"x": 1' in r.stdout


@respx.mock
def test_credits_balance(monkeypatch):
    monkeypatch.setenv("TALONIC_API_KEY", "tlnc_x")
    respx.get("https://api.talonic.com/v1/credits/balance").mock(
        return_value=httpx.Response(200, json={"balance_credits": 500})
    )
    r = runner.invoke(app, ["credits", "balance"])
    assert r.exit_code == 0
    assert "500" in r.stdout
