"""Talonic CLI built on Typer.

Reads TALONIC_API_KEY from env; JSON to stdout, errors to stderr, exit codes
0 (ok) / 1 (SDK error) / 2 (usage)."""

from __future__ import annotations

import json
import sys
from typing import Any

import typer

from talonic import Talonic, __version__
from talonic.errors import TalonicError

app = typer.Typer(
    help="Talonic CLI — extract structured data from documents.", no_args_is_help=True
)
schemas_app = typer.Typer(help="Schema management")
docs_app = typer.Typer(help="Document operations")
extractions_app = typer.Typer(help="Extraction operations")
credits_app = typer.Typer(help="Credit balance")
app.add_typer(schemas_app, name="schemas")
app.add_typer(docs_app, name="documents")
app.add_typer(extractions_app, name="extractions")
app.add_typer(credits_app, name="credits")


def _emit(value: Any, *, pretty: bool = False) -> None:  # noqa: ANN401
    if isinstance(value, str):
        sys.stdout.write(value)
        if not value.endswith("\n"):
            sys.stdout.write("\n")
    else:
        sys.stdout.write(json.dumps(value, indent=2 if pretty else None, default=str))
        sys.stdout.write("\n")


def _fail(message: str, status: int = 1) -> None:
    sys.stderr.write(message + "\n")
    raise typer.Exit(code=status)


def _client() -> Talonic:
    try:
        return Talonic()
    except TalonicError as exc:
        _fail(str(exc))
        raise  # appease mypy


@app.callback(invoke_without_command=True)
def root(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", help="Print version and exit"),
) -> None:
    if version:
        _emit(f"talonic {__version__}")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        _emit(ctx.get_help())


# === schemas ===
@schemas_app.command("list")
def schemas_list(pretty: bool = typer.Option(False, "--pretty")) -> None:
    _emit(_client().schemas.list().data, pretty=pretty)


@schemas_app.command("get")
def schemas_get(schema_id: str, pretty: bool = typer.Option(False, "--pretty")) -> None:
    _emit(_client().schemas.get(schema_id).data, pretty=pretty)


@schemas_app.command("delete")
def schemas_delete(schema_id: str) -> None:
    _emit(_client().schemas.delete(schema_id).data)


# === documents ===
@docs_app.command("list")
def docs_list(
    limit: int | None = typer.Option(None),
    status: str | None = typer.Option(None),
    search: str | None = typer.Option(None),
    pretty: bool = typer.Option(False, "--pretty"),
) -> None:
    _emit(_client().documents.list(limit=limit, status=status, search=search).data, pretty=pretty)


@docs_app.command("get")
def docs_get(document_id: str, pretty: bool = typer.Option(False, "--pretty")) -> None:
    _emit(_client().documents.get(document_id).data, pretty=pretty)


@docs_app.command("markdown")
def docs_markdown(document_id: str) -> None:
    r = _client().documents.get_markdown(document_id).data
    _emit(r.get("markdown", "") if isinstance(r, dict) else r)


@docs_app.command("delete")
def docs_delete(document_id: str) -> None:
    _emit(_client().documents.delete(document_id).data)


# === extractions ===
@extractions_app.command("get")
def extractions_get(
    extraction_id: str,
    format: str | None = typer.Option(None, "--format"),
    pretty: bool = typer.Option(False, "--pretty"),
) -> None:
    client = _client()
    if format == "csv":
        _emit(client.extractions.get_data(extraction_id, format="csv"))
    else:
        _emit(client.extractions.get_data(extraction_id).data, pretty=pretty)


# === credits ===
@credits_app.command("balance")
def credits_balance(pretty: bool = typer.Option(False, "--pretty")) -> None:
    _emit(_client().credits.get_balance().data, pretty=pretty)


# === extract ===
@app.command()
def extract(
    file: str | None = typer.Argument(None),
    file_url: str | None = typer.Option(None, "--file-url"),
    document_id: str | None = typer.Option(None, "--document-id"),
    schema: str | None = typer.Option(None, help="Inline JSON schema"),
    schema_id: str | None = typer.Option(None, "--schema-id"),
    pretty: bool = typer.Option(False, "--pretty"),
) -> None:
    parsed_schema = json.loads(schema) if schema else None
    try:
        result = _client().extract(
            file_path=file,
            file_url=file_url,
            document_id=document_id,
            schema=parsed_schema,
            schema_id=schema_id,
        )
    except TalonicError as exc:
        _fail(str(exc))
        raise
    _emit(result.data, pretty=pretty)


# === search ===
@app.command()
def search(
    query: str,
    limit: int | None = typer.Option(None),
    pretty: bool = typer.Option(False, "--pretty"),
) -> None:
    _emit(_client().search(query, limit=limit).data, pretty=pretty)
