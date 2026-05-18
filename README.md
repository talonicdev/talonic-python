# talonic

Official Talonic SDK for Python. Extract structured, schema-validated data from any document.

[![CI](https://github.com/talonicdev/talonic-python/actions/workflows/ci.yml/badge.svg)](https://github.com/talonicdev/talonic-python/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/talonic.svg)](https://pypi.org/project/talonic/)
[![Python](https://img.shields.io/pypi/pyversions/talonic.svg)](https://pypi.org/project/talonic/)
[![License](https://img.shields.io/pypi/l/talonic.svg)](https://github.com/talonicdev/talonic-python/blob/main/LICENSE)

> **Looking for the AI-agent / MCP path?** [`@talonic/mcp`](https://github.com/talonicdev/talonic-mcp) wraps the Talonic API as a Model Context Protocol server. Easiest install on Claude.ai is the hosted endpoint at `https://mcp.talonic.com/mcp`. For Node SDK consumers, see [`@talonic/node`](https://github.com/talonicdev/talonic-node).

## Install

```bash
pip install talonic
```

Requires Python 3.10 or newer. Three runtime deps: `httpx`, `pydantic`, `typer`.

## Quickstart

```python
from talonic import Talonic

client = Talonic(api_key="tlnc_...")  # or set TALONIC_API_KEY env var

result = client.extract(
    file_path="./invoice.pdf",
    schema={
        "type": "object",
        "properties": {
            "vendor_name": {"type": "string"},
            "total_amount": {"type": "number"},
            "due_date":     {"type": "string", "format": "date"},
        },
        "required": ["vendor_name", "total_amount"],
    },
)

print(result.data)              # {'vendor_name': 'Acme Corp', 'total_amount': 14250, 'due_date': '2026-03-15'}
print(result.confidence.overall) # 0.97
print(result.cost)               # CostInfo(cost_credits=12, cost_eur=0.024, ...)
print(result.rate_limit)         # RateLimitInfo(limit=100, remaining=99, reset_at=…) | None
```

## Async

```python
import asyncio
from talonic import AsyncTalonic

async def main():
    async with AsyncTalonic(api_key="tlnc_...") as client:
        result = await client.extract(file_path="./invoice.pdf", schema={...})
        print(result.data)

asyncio.run(main())
```

## API surface

26 operations across 8 categories. Direct sibling of `@talonic/node@0.1.x`:

| Category | Methods |
| --- | --- |
| top-level | `extract()`, `search()` |
| `documents` | `list`, `get`, `get_markdown`, `re_extract`, `delete`, `filter` |
| `extractions` | `list`, `get`, `get_data`, `patch` |
| `fields` | `list`, `get`, `similar` |
| `jobs` | `create`, `list`, `get`, `get_results`, `cancel` |
| `schemas` | `list`, `get`, `create`, `update`, `delete` |
| `credits` | `get_balance` |

See [docs](https://github.com/talonicdev/talonic-python#api-surface) for full signatures.

## CLI

```bash
talonic --version
talonic schemas list
talonic documents list --limit=20
talonic credits balance
talonic extract ./invoice.pdf --schema='{"type":"object",...}'
talonic search "indemnification clauses"
```

The `talonic` binary name overlaps with `@talonic/node`'s CLI. If both are installed globally, PATH order picks the winner; `python -m talonic` forces the Python CLI.

## Configuration

```python
client = Talonic(
    api_key=...,                        # or TALONIC_API_KEY env
    base_url="https://api.talonic.com", # default; or TALONIC_BASE_URL
    timeout=60.0,                       # per-request seconds
    max_retries=3,                      # 429/500-504/network/timeout
)
```

## Errors

```python
from talonic import (
    TalonicError, TalonicAuthError, TalonicNotFoundError, TalonicValidationError,
    TalonicRateLimitError, TalonicServerError, TalonicNetworkError, TalonicTimeoutError,
)

try:
    client.extract(...)
except TalonicRateLimitError as exc:
    print(f"Reset at {exc.rate_limit.reset_at}")
except TalonicError as exc:
    print(f"{exc.code} (status {exc.status}, request {exc.request_id}): {exc.message}")
```

## Development

```bash
git clone https://github.com/talonicdev/talonic-python
cd talonic-python
make install        # editable install + pre-commit hook
make test           # unit + CLI + models
make typecheck      # mypy --strict
make lint           # ruff
make models         # regenerate Pydantic models from openapi.json
make build          # sdist + wheel
TALONIC_API_KEY=tlnc_... make test-live   # opt-in integration
```

## License

MIT (c) Talonic GmbH
