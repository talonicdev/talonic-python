#!/usr/bin/env python3
"""Generate Pydantic v2 models from @talonic/docs/openapi.json.

Output: src/talonic/_models/<topic>.py — one file per OpenAPI tag.
The output is committed to git; this script is idempotent.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SPEC = REPO / "node_modules" / "@talonic" / "docs" / "openapi.json"
OUT_DIR = REPO / "src" / "talonic" / "_models"
# datamodel-codegen writes to a single file when the output path is a .py file.
OUT_FILE = OUT_DIR / "models.py"


def main() -> int:
    if not SPEC.exists():
        print(f"error: spec not found at {SPEC}; run `npm install` first", file=sys.stderr)
        return 2

    # Preserve __init__.py while regenerating.
    init_py = (OUT_DIR / "__init__.py").read_text() if (OUT_DIR / "__init__.py").exists() else ""
    # Remove only the generated models file, not the entire directory.
    if OUT_FILE.exists():
        OUT_FILE.unlink()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "__init__.py").write_text(
        init_py or '"""Generated Pydantic models. Do not edit."""\n'
    )

    cmd = [
        "datamodel-codegen",
        "--input",
        str(SPEC),
        "--input-file-type",
        "openapi",
        "--output",
        str(OUT_FILE),
        "--output-model-type",
        "pydantic_v2.BaseModel",
        "--target-python-version",
        "3.10",
        "--use-union-operator",
        "--use-standard-collections",
        "--use-schema-description",
        "--use-field-description",
        "--field-constraints",
        "--snake-case-field",
        "--reuse-model",
        "--disable-timestamp",
    ]
    print("$", " ".join(cmd))
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        return result.returncode

    # Ruff-format and lint-fix the generated output.
    for cmd in (
        ["ruff", "format", str(OUT_DIR)],
        ["ruff", "check", "--fix", "--unsafe-fixes", str(OUT_DIR)],
    ):
        subprocess.run(cmd, check=False)

    print(f"\n✓ Models generated at {OUT_DIR.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
