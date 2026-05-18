# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-05-XX

### Added

- Initial release. Mirrors `@talonic/node@0.1.x` (26 ops across 8 categories) with both sync (`Talonic`) and async (`AsyncTalonic`) clients.
- Hybrid build: Pydantic v2 response models generated from `@talonic/docs/openapi.json` via `datamodel-code-generator`; hand-written transport, resources, and CLI.
- `talonic` CLI built on Typer (`talonic schemas list`, `talonic extract …`, `talonic search …`, `talonic credits balance`, etc.).
- PyPI Trusted Publisher (OIDC) — no long-lived secrets.
- CI: lint (`ruff`), typecheck (`mypy --strict`), spec-drift check, tests across Python 3.10/3.11/3.12/3.13 on Ubuntu + macOS.

### Known limitations (v0.1.0)

- `extract()` requires either a `schema` or `schema_id` (auto-populates `required` from `properties` when missing — same guardrail as `@talonic/node`).
- `is_not_empty` filter checks materialized values; expect a few seconds' lag after extraction for batch documents.
- API coverage matches Node SDK (~18% of the full spec); broader SDK expansion planned for v0.2.
