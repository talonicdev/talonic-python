#!/usr/bin/env python3
"""CI drift check: regenerate models and fail if `git status` shows changes.

If this fails, run `make models` locally and commit the diff.
"""

from __future__ import annotations

import subprocess
import sys


def main() -> int:
    # Regenerate.
    r = subprocess.run([sys.executable, "scripts/generate_models.py"], check=False)
    if r.returncode != 0:
        print("error: model generation failed", file=sys.stderr)
        return r.returncode

    # Diff src/talonic/_models against the index.
    diff = subprocess.run(
        ["git", "diff", "--exit-code", "--", "src/talonic/_models"],
        check=False,
    )
    if diff.returncode != 0:
        print(
            "error: generated models drifted from committed copies. "
            "Run `make models` and commit the result.",
            file=sys.stderr,
        )
        return 1
    print("✓ generated models match committed copies")
    return 0


if __name__ == "__main__":
    sys.exit(main())
