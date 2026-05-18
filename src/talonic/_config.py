"""TalonicConfig: client construction options with env-driven defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from talonic.errors import TalonicValidationError


@dataclass
class TalonicConfig:
    """Configuration for a Talonic / AsyncTalonic client.

    Args:
        api_key:     Talonic API key (starts with "tlnc_"). Falls back to $TALONIC_API_KEY.
        base_url:    API base URL. Falls back to $TALONIC_BASE_URL, then "https://api.talonic.com".
        timeout:     Per-request timeout in seconds. Default 60.
        max_retries: Retries on 429/500-504/network/timeout. Default 3.
        transport:   Optional httpx transport for testing (e.g. httpx.MockTransport).
    """

    api_key: str | None = None
    base_url: str | None = None
    timeout: float = 60.0
    max_retries: int = 3
    transport: Any = None  # httpx.BaseTransport | httpx.AsyncBaseTransport | None

    def __post_init__(self) -> None:
        # API key: explicit > env > error.
        if not self.api_key:
            env_key = os.environ.get("TALONIC_API_KEY", "").strip()
            if not env_key:
                raise TalonicValidationError(
                    message="TALONIC_API_KEY is required (pass api_key=... or set the env var).",
                    code="MISSING_API_KEY",
                )
            self.api_key = env_key

        # Base URL: explicit > env > default. Strip trailing slashes.
        if not self.base_url:
            self.base_url = os.environ.get("TALONIC_BASE_URL", "https://api.talonic.com")
        assert self.base_url is not None
        self.base_url = self.base_url.rstrip("/")
