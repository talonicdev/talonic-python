# Talonic Python SDK — v0.1.0 Design

| | |
| --- | --- |
| **Date** | 2026-05-18 |
| **Status** | Draft — pending user review |
| **Owner** | Hamlet Hayrapetyan |
| **Implementer** | Claude (this session and follow-ups) |
| **Target version** | `talonic 0.1.0` on PyPI |
| **Repo** | `github.com/talonicdev/talonic-python` |

## Summary

Build `@talonic/node`'s sibling for Python — `talonic` on PyPI. Same API surface, same ergonomics, snake_case'd, with both sync and async clients. Hybrid build: generate Pydantic v2 response models from `@talonic/docs/openapi.json`, hand-write the client surface (transport, resources, CLI). Scope is exact Node-SDK parity (26 operations across 8 categories). Standalone repo, PyPI Trusted Publisher (OIDC) for releases, no long-lived secrets. Target ~1 week of hand-written work plus a polish/test pass.

## Goals

- Python developers building data pipelines, notebooks, AI-agent frameworks (LangChain/LlamaIndex/CrewAI/Haystack), or backend services get the same SDK quality Node developers get today.
- Both sync and async surfaces from day one, with identical method names and return shapes.
- Type-safe end to end: Pydantic v2 response models, hand-written request shapes, `mypy --strict` clean.
- Lock-step with the OpenAPI spec via CI drift check, same pattern as `@talonic/node`'s `npm run check:spec`.
- Distribution as low-friction as the Node SDK: `pip install talonic`, single binary `talonic` for CLI usage.

## Non-goals (v0.1.0)

- **No MCP server in Python.** The hosted MCP at `mcp.talonic.com` already serves every agent; `npx -y @talonic/mcp@latest` covers local installs. Two MCP implementations would double maintenance for zero new audience. Re-evaluate if a specific Python-shop user reports needing it.
- **No API expansion beyond Node SDK parity.** The Talonic API has ~154 paths across 30 resource groups; the Node SDK exposes ~18% of that surface. The Python SDK matches Node coverage. Closing the larger API gap is a follow-up that should land in `@talonic/node` first (or simultaneously), so the two SDKs stay aligned.
- **No code generation for the client surface.** Only response models are generated. The hand-tuned ergonomics (`extract()` file-source union, `autoPopulateRequired`, `WithRateLimit[T]`, error hierarchy) stay hand-written.
- **No deep website integration on day one.** README on GitHub + auto-rendered README on PyPI are sufficient discovery surface for v0.1.

## Decisions log

| Decision | Choice | Alternatives considered |
| --- | --- | --- |
| Target audience | All three: data/ML notebooks, AI-framework integrators, backend service developers — full parity with Node SDK | Notebooks-only; agent-frameworks-only; backend-only |
| Author approach | Hybrid: generate Pydantic models from OpenAPI; hand-write client surface | Hand-write everything; fully generated client |
| Repo location | Standalone `github.com/talonicdev/talonic-python` | Subdirectory of `talonic-node`; inside `platform` monorepo |
| PyPI name | `talonic` (`pip install talonic`, `from talonic import Talonic`) | `talonic-sdk`; `talonic-python` |
| Minimum Python | 3.10+ | 3.9+; 3.11+ |
| v0.1.0 scope | Exact Node-SDK parity (26 ops, 8 categories) | + obvious user-facing gaps; full spec parity |
| Sync/async surface | Both, parallel class hierarchies, shared private logic | Async-only; sync-only; `unasync` auto-generation |
| Build backend | `hatchling` | `setuptools`; `poetry`; `flit` |
| HTTP client | `httpx` (sync + async same API) | `requests` + `aiohttp`; pure stdlib |
| Validation | Pydantic v2 | Pydantic v1; attrs; dataclasses |
| CLI tool | `typer` | bare `click`; `argparse`; `cyclopts` |
| Codegen tool | `datamodel-code-generator` (models only) | `openapi-python-client` (full client); custom |
| Release auth | PyPI Trusted Publisher (OIDC), no long-lived tokens | API token in GitHub secrets |
| Versioning | Semver, auto-bump patch on every src/docs change | Manual versioning |
| Test runner | `pytest` + `pytest-asyncio` (`asyncio_mode=auto`) + `respx` for HTTP mocking | `unittest`; `pytest-httpx` |
| Lint/format | `ruff` (replaces black + isort + flake8) + `mypy --strict` | `black` + `isort` + `flake8` |

## Architecture & layering

```
src/talonic/
├── __init__.py          # Public exports: Talonic, AsyncTalonic, errors, types
├── _version.py          # Single source of truth for version
├── _http.py             # Sync + async httpx transports; retry, backoff, header parsing
├── _config.py           # TalonicConfig dataclass (api_key, base_url, timeout, max_retries)
├── _models/             # GENERATED — Pydantic v2 models from openapi.json
│   ├── __init__.py
│   ├── document.py      # Document, DocumentTriage, DocumentList, …
│   ├── extraction.py    # Extraction, ExtractionData, …
│   ├── schema.py        # Schema (response shape — not the JSON-Schema dict)
│   ├── job.py
│   ├── field.py
│   ├── search.py
│   └── credits.py       # EnhancedBalance, CostInfo, …
├── _types/              # Hand-written request/wrapper types
│   ├── __init__.py
│   ├── rate_limit.py    # RateLimitInfo, WithRateLimit[T] generic
│   ├── cost.py          # CostInfo (parsed from X-Talonic-Cost-* headers)
│   └── extract_input.py # ExtractInput discriminated union
├── errors.py            # TalonicError hierarchy
├── resources/
│   ├── __init__.py
│   ├── _base.py         # Param-builder helpers shared between sync + async
│   ├── credits.py       # Credits + AsyncCredits
│   ├── documents.py     # Documents + AsyncDocuments
│   ├── extractions.py   # Extractions + AsyncExtractions
│   ├── fields.py        # Fields + AsyncFields
│   ├── jobs.py          # Jobs + AsyncJobs
│   └── schemas.py       # Schemas + AsyncSchemas
├── client.py            # Talonic + AsyncTalonic (the user-facing entry points)
└── cli.py               # Typer CLI app

scripts/
├── generate_models.py   # Runs datamodel-code-generator over openapi.json
└── check_spec.py        # CI drift check: regenerate models, fail if diff
```

**Layer responsibilities:**

- **`_http.py`** — the only HTTP boundary. Handles retries (429, 500-504, network, timeout), exponential backoff with jitter capped at 16s, multipart serialisation, `X-RateLimit-*` and `X-Talonic-Cost-*` header parsing. Two flavors: `SyncTransport` and `AsyncTransport` sharing a `BaseTransport` mixin for pure-function helpers (header building, retry-decision logic, header parsing).
- **`_models/`** — generated, never edited by hand. Idempotent regeneration via `scripts/generate_models.py`. Pre-commit hook + CI drift check guard against drift.
- **`_types/`** — hand-written wrappers and request shapes that don't correspond to OpenAPI schemas (header-derived `RateLimitInfo`/`CostInfo`, the file-source discriminated union on `extract()`).
- **`resources/`** — hand-written, one module per category. Each module defines `_FooBase` (pure param-builders, no I/O), `Foo` (sync, takes `SyncTransport`), and `AsyncFoo` (async, takes `AsyncTransport`).
- **`client.py`** — `Talonic` and `AsyncTalonic` wire transport + resources together. Read `TALONIC_API_KEY` from env when no `api_key` is passed.
- **`cli.py`** — Typer app with subcommands. Reads env, calls into `Talonic` (sync only — async makes no sense in a CLI invocation).
- **`errors.py`** — `TalonicError` hierarchy matching Node's eight error classes.

## Public API surface

Mirrors `@talonic/node@0.1.16` exactly, with snake_case. 26 operations across 8 categories.

```python
from talonic import Talonic, AsyncTalonic

client = Talonic(api_key="tlnc_...")  # or TALONIC_API_KEY env var

# === Top-level (2 ops) ===
result = client.extract(file_path="./invoice.pdf", schema={...})
result.data            # extracted fields (dict[str, Any])
result.confidence.overall
result.cost            # CostInfo | None — credits, EUR, post-call balance
result.rate_limit      # RateLimitInfo | None

hits = client.search("indemnification clauses", limit=10)
hits.documents
hits.field_matches     # each .filterable: bool
hits.sources
hits.schemas
hits.fields

# === documents (6 ops) ===
client.documents.list(limit=50, status="completed", source_id=..., search=..., cursor=...)
client.documents.get("doc_id")
client.documents.get_markdown("doc_id")
client.documents.re_extract("doc_id")
client.documents.delete("doc_id")
client.documents.filter(conditions=[{"field": "vendor.name", "operator": "is_not_empty"}], ...)

# === extractions (4 ops) ===
client.extractions.list(document_id="doc_id")
client.extractions.get("extraction_id")
client.extractions.get_data("extraction_id")               # → dict
client.extractions.get_data("extraction_id", format="csv") # → str (overload)
client.extractions.patch("extraction_id", corrections=[...])

# === fields (3 ops) ===
client.fields.list(search="vendor", tier="t1", limit=50)
client.fields.get("field_id")
client.fields.similar("field_id", limit=10)  # nearest-neighbour lookup

# === jobs (5 ops) ===
client.jobs.create(schema_id="...", document_ids=[...])
client.jobs.list()
client.jobs.get("job_id")
client.jobs.get_results("job_id")
client.jobs.cancel("job_id")

# === schemas (5 ops) ===
client.schemas.list()
client.schemas.get("schema_id")       # UUID or SCH-XXXXXXXX
client.schemas.create(name="Invoice", definition={...})
client.schemas.update("schema_id", name="Invoice v2")
client.schemas.delete("schema_id")

# === credits (1 op) ===
client.credits.get_balance()
# → EnhancedBalance(balance_credits, balance_eur, burn_rate_30d_credits,
#                   projected_runway_days, tier, tier_resets_at)
```

**Async surface — identical method names, prefixed with `await`:**

```python
async with AsyncTalonic(api_key="tlnc_...") as client:
    result = await client.extract(file_path="./invoice.pdf", schema={...})
    docs = await client.documents.list(limit=50)
    hits = await client.search("indemnification clauses")
```

**File-source union on `extract()` only** (matches Node SDK: `documents.get_markdown(id)` accepts only a document id) — keyword-only, exactly one of:

- `file_data: bytes` + `filename: str` (in-memory bytes)
- `file_path: str | os.PathLike` (local file)
- `file_url: str` (publicly reachable URL)
- `document_id: str` (existing Talonic document — cheapest path, re-extract)

Multiple sources, or none, raises `TalonicValidationError` immediately, before any HTTP call.

**`autoPopulateRequired` guardrail** — when caller passes a JSON Schema with `properties` but no `required`, the SDK silently fills `required` with all property keys before sending. Prevents the silent-empty-data footgun the Node SDK has.

**Error hierarchy:**

```
TalonicError                  # base
├── TalonicAuthError          # 401, 403
├── TalonicNotFoundError      # 404
├── TalonicValidationError    # 400, 409, 413, 422
├── TalonicRateLimitError     # 429 (after retries) — has .rate_limit
├── TalonicServerError        # 500–504 (after retries)
├── TalonicNetworkError       # DNS / TCP failures
└── TalonicTimeoutError       # request exceeded timeout
```

Every error has `.status`, `.code`, `.request_id`, `.message`. Same shape as Node SDK.

**`WithRateLimit[T]`** — generic Pydantic-friendly dataclass returned by every successful call. `rate_limit: RateLimitInfo | None` (None when no `X-RateLimit-*` headers were present, matching Node 0.1.8+ behavior).

**`CostInfo`** — populated on `extract()` calls that actually run an extraction (not on read-only endpoints, and `None` when the API reports no cost). Parsed from `X-Talonic-Cost-*` and `X-Talonic-Balance-*` response headers.

## Sync + async strategy

**Parallel class hierarchies sharing pure-function helpers**:

```python
class BaseTransport:
    """Pure functions, no I/O."""
    def _build_headers(self, api_key: str) -> dict[str, str]: ...
    def _should_retry(self, status: int, attempt: int, body: dict | None) -> bool: ...
    def _backoff_delay(self, attempt: int) -> float: ...
    def _parse_rate_limit(self, headers) -> RateLimitInfo | None: ...
    def _parse_cost(self, headers) -> CostInfo | None: ...

class SyncTransport(BaseTransport):
    def __init__(self, config: TalonicConfig): self._client = httpx.Client(...)
    def request(self, method, path, **kwargs) -> WithRateLimit[Any]: ...

class AsyncTransport(BaseTransport):
    def __init__(self, config: TalonicConfig): self._client = httpx.AsyncClient(...)
    async def request(self, method, path, **kwargs) -> WithRateLimit[Any]: ...
```

Resources follow the same pattern with `_FooBase` (pure param builders) + `Foo` (sync) + `AsyncFoo` (async).

**Rejected alternatives:**

- `unasync`-style codegen — fragile, painful to debug, drifts from edits.
- Single resource class with runtime-swapped transport — breaks type checking and `with`/`async with` ergonomics.
- Async-only with `asyncio.run()` shim — breaks notebooks already running an event loop.

**Cost:** ~2x the lines per resource module vs single-flavor. For 8 categories × ~5 methods, manageable. **Benefit:** guaranteed behavioral parity (one test logic runs against both flavors via `pytest.mark.parametrize`).

## Models & codegen

**Tool: `datamodel-code-generator`** (`pip install datamodel-code-generator`). Generates Pydantic v2 BaseModel classes from `openapi.json` → one file per OpenAPI tag in `src/talonic/_models/`.

**Spec source: `@talonic/docs`** npm package, pinned as a dev dep (`package.json` in the repo, just like `talonic-node` does it). Vendored alongside the Python tooling.

**Regeneration workflow:**

```bash
make models                                # alias for:
python scripts/generate_models.py          # idempotent, fully reproducible
ruff format src/talonic/_models/
ruff check --fix src/talonic/_models/
```

Models are committed to git. **Never hand-edited.** Pre-commit hook + CI drift check guard against drift. The CI step regenerates models in-place and runs `git diff --exit-code -- src/talonic/_models/`; failing the build means someone modified the spec or the models manually and the two no longer match.

**End users never run `datamodel-code-generator`.** Pre-generated models ship in the wheel.

## CLI

**Tool: `typer`.** Generates help/parsing from Python type hints, ergonomic for typed SDKs.

```bash
talonic --version
talonic --help

talonic schemas list
talonic schemas get <schema-id>          # UUID or SCH-XXXXXXXX
talonic schemas delete <schema-id>

talonic documents list --limit=20 --status=completed
talonic documents get <doc-id>
talonic documents markdown <doc-id>
talonic documents delete <doc-id>

talonic extract ./invoice.pdf --schema='{"type":"object",...}'
talonic extract --document-id <doc-id> --schema-id <schema-id>
talonic extract --file-url https://example.com/i.pdf --schema-id <schema-id>

talonic search "indemnification clauses" --limit=10
talonic credits balance

talonic extractions get <id> --format=csv > out.csv
```

**Conventions:**

- Reads `TALONIC_API_KEY` from env.
- Reads `TALONIC_BASE_URL` for overrides.
- JSON-to-stdout by default, `--pretty` for human formatting.
- Exit codes: `0` ok, `1` SDK error (with stderr message), `2` usage error.
- Errors to stderr, data to stdout (Unix idiom).

**Binary name `talonic` (same as Node CLI).** README documents the collision risk: if both packages are globally installed, PATH order determines which `talonic` resolves first. Workaround: `python -m talonic <cmd>`.

## Distribution & release pipeline

### `pyproject.toml`

```toml
[build-system]
requires = ["hatchling>=1.21"]
build-backend = "hatchling.build"

[project]
name = "talonic"
dynamic = ["version"]
requires-python = ">=3.10"
license = "MIT"
authors = [{ name = "Talonic GmbH", email = "info@talonic.ai" }]
readme = "README.md"
dependencies = [
  "httpx>=0.27",
  "pydantic>=2.6",
  "typer>=0.12",
]

[project.optional-dependencies]
dev = [
  "pytest>=8",
  "pytest-asyncio>=0.23",
  "respx>=0.20",
  "ruff>=0.5",
  "mypy>=1.10",
  "datamodel-code-generator>=0.25",
  "hatch>=1.12",
  "build>=1.2",
]

[project.scripts]
talonic = "talonic.cli:app"
```

### CI workflow (`.github/workflows/ci.yml`)

Runs on PR and push to main. Matrix: Python 3.10/3.11/3.12/3.13 × ubuntu/macos.

Steps: checkout → setup-python → `pip install -e ".[dev]"` → `ruff format --check` → `ruff check` → `mypy src/talonic` → `python scripts/check_spec.py` → `pytest -q` → `python -m build`.

Target wall time: <90s per matrix cell.

### Publish workflow (`.github/workflows/publish.yml`)

Trigger: push to main when `src/**`, `pyproject.toml`, or `docs/**` change.

Permissions: `id-token: write` (for PyPI OIDC), `contents: write` (for the `chore: bump` push).

Steps:

1. Checkout, setup Python 3.12, install build tools.
2. Auto-bump patch version if `_version.py` value matches the latest on PyPI. Commit `chore: bump talonic to X.Y.Z [skip ci]`.
3. `python -m build` → produces sdist + wheel.
4. `pypa/gh-action-pypi-publish@release/v1` — no token, uses Trusted Publisher OIDC.
5. (Optional, deferred) Trigger website rebuild via `repository_dispatch`.

**No `PYPI_TOKEN` secret. No long-lived credentials.** PyPI mints a short-lived token from the GitHub OIDC claim at publish time.

### Versioning

Semver. Auto-bump patch via CI on every src/docs change. Manual version bumps for minor (new features) and major (breaking). `src/talonic/_version.py` is the single source of truth (Hatch reads it via `[tool.hatch.version]`).

## Prerequisites

| # | Item | Status |
| --- | --- | --- |
| 1 | Empty repo `talonicdev/talonic-python` | ✅ exists |
| 2 | PyPI organization for `talonicdev` | ⏳ submitted, pending PyPI approval |
| 3 | PyPI project name `talonic` reserved + Trusted Publisher wired to `publish.yml` | Pending #2 approval |
| 4 | TestPyPI mirror (`test.pypi.org`) — same setup as #3 | Pending #2 approval |
| 5 | `@talonic/docs` npm spec pin | Will be configured in `package.json` during impl |
| 6 | GitHub repo secrets | **None required** (PyPI OIDC + GITHUB_TOKEN cover all auth) |

## Testing strategy

- **Framework:** `pytest` + `pytest-asyncio` (`asyncio_mode = "auto"`) + `respx` for HTTP mocking.
- **Lint/typecheck:** `ruff format` + `ruff check` + `mypy --strict`.

| Category | Count target | Location |
| --- | ---: | --- |
| Unit (resource methods, transport, retry, errors, type wrappers) | ~250 | `tests/unit/` |
| Sync/async parametrized parity (same logic, both flavors) | doubles unit count | shared fixtures |
| CLI | ~20 | `tests/cli/` |
| Model round-trip (real prod responses → Pydantic validates) | ~30 | `tests/models/` |
| Live (opt-in, real API key, nightly cron) | ~15 | `tests/live/` |
| Smoke (import, version match, CLI `--version`) | ~5 | `tests/smoke.py` |
| **Total v0.1.0 target** | **~500** | |

**Coverage target:** ≥90% on `src/talonic/` excluding `_models/`.

**Sync/async parametrization shape:**

```python
@pytest.fixture(params=["sync", "async"])
async def docs(request, respx_mock):
    if request.param == "sync":
        client = Talonic(api_key="tlnc_test")
        yield client.documents, "sync"
    else:
        async with AsyncTalonic(api_key="tlnc_test") as client:
            yield client.documents, "async"

async def test_list(docs, respx_mock):
    resource, flavor = docs
    respx_mock.get("/v1/documents").respond(200, json={"data": [...]})
    result = resource.list() if flavor == "sync" else await resource.list()
    assert len(result.data) == 3
```

**Live tests:** `pytest tests/live/ --live` (defaults to skip). Reads `TALONIC_API_KEY`, fails loud if missing. Runs nightly on a cron in CI, not on every PR.

## Acceptance criteria for v0.1.0

1. `pip install talonic` from PyPI works on Python 3.10/3.11/3.12/3.13 (Linux + macOS).
2. `from talonic import Talonic, AsyncTalonic` and the 26 documented operations all behave per the Node SDK contract.
3. `mypy --strict src/talonic/` passes.
4. `ruff format --check` and `ruff check` pass.
5. `pytest` passes with ≥90% coverage.
6. `python scripts/check_spec.py` exits 0 against the pinned `@talonic/docs` version.
7. `talonic --version` CLI prints the correct version and exits 0.
8. Live test suite (run manually with a real `tlnc_` key) round-trips a real PDF extraction end-to-end.
9. README cross-links to `@talonic/node`, `@talonic/mcp`, and `talonic.com`.
10. CHANGELOG documents the v0.1.0 release.

## Open questions for engineering

1. **PyPI org email/owner.** Who at Talonic owns the PyPI organization? Affects #2 above.
2. **Naming for the CLI binary collision.** Confirm Hamlet's call (keep `talonic`, document the collision) holds when engineering reviews — or rename to `talonic-py`.
3. **Spec source choice.** Should the Python SDK consume `@talonic/docs` as an npm package (same as Node SDK does), or should we publish the OpenAPI spec to PyPI / a public URL so the Python repo doesn't need Node tooling for codegen? Current spec assumes the former.
4. **Website docs surface.** Deferred per v0.1 scope, but should be a Q2/Q3 follow-up: build `talonic.com/docs/python` analogous to `/docs/sdk` and `/docs/mcp`, wired via the same `WEBSITE_DISPATCH_TOKEN` pattern.
5. **Test PyPI gating.** Should the publish workflow also push to TestPyPI on every main push (cheap rehearsal), or only when explicitly tagged?

## Out of scope, explicitly deferred

- **Python MCP server.** Hosted MCP + `npx` cover the audience.
- **API coverage beyond Node SDK parity** (~126 of the 154 spec paths). Belongs in a coordinated SDK-expansion sprint that also updates `@talonic/node`.
- **Streaming responses** (SSE, partial extracts). API doesn't expose any streaming endpoints today.
- **Webhook signature verification helpers.** Belongs in the SDK eventually but not v0.1.
- **Pre-signed upload URL workflow.** Tracked separately for the MCP server; not relevant for direct SDK consumers who can pass `file_data` or `file_path`.
- **Locale / I18n.** Error messages in English only for v0.1.

## Implementation order (preview for the writing-plans step)

1. Scaffold repo: `pyproject.toml`, `src/talonic/`, `.github/workflows/`, `pre-commit`, `ruff` + `mypy` config.
2. Wire `@talonic/docs` spec pin + `scripts/generate_models.py` + the drift CI check. Commit empty `_models/` shell.
3. `_http.py` — sync + async transport, retry, header parsing. Tests.
4. `errors.py`, `_types/`. Tests.
5. Resources one at a time, in this order (highest leverage first): `schemas` → `credits` → `documents` → `extractions` → `fields` → `jobs` → top-level `search` → top-level `extract` (most complex due to file-source union). Each ships with sync + async + tests.
6. CLI (`cli.py`) — wires existing resources, no new logic.
7. Live tests against production.
8. README, CHANGELOG, v0.1.0 PyPI publish.
9. Cross-link: update Node SDK README and MCP README to reference the Python SDK.

Total target: ~5 working days for the core SDK, +2 days for CLI + tests + docs. Live-test pass + PyPI publish on day 7.
