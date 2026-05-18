"""TalonicConfig: env-driven defaults, explicit overrides, validation."""

import pytest

from talonic._config import TalonicConfig
from talonic.errors import TalonicValidationError


def test_explicit_api_key():
    cfg = TalonicConfig(api_key="tlnc_abc")
    assert cfg.api_key == "tlnc_abc"
    assert cfg.base_url == "https://api.talonic.com"
    assert cfg.timeout == 60.0
    assert cfg.max_retries == 3


def test_env_api_key(monkeypatch):
    monkeypatch.setenv("TALONIC_API_KEY", "tlnc_env")
    cfg = TalonicConfig()
    assert cfg.api_key == "tlnc_env"


def test_env_base_url(monkeypatch):
    monkeypatch.setenv("TALONIC_API_KEY", "tlnc_x")
    monkeypatch.setenv("TALONIC_BASE_URL", "http://localhost:3001")
    cfg = TalonicConfig()
    assert cfg.base_url == "http://localhost:3001"


def test_explicit_overrides_env(monkeypatch):
    monkeypatch.setenv("TALONIC_API_KEY", "tlnc_env")
    cfg = TalonicConfig(api_key="tlnc_explicit")
    assert cfg.api_key == "tlnc_explicit"


def test_missing_api_key_raises(monkeypatch):
    monkeypatch.delenv("TALONIC_API_KEY", raising=False)
    with pytest.raises(TalonicValidationError, match="TALONIC_API_KEY"):
        TalonicConfig()


def test_base_url_trailing_slash_stripped():
    cfg = TalonicConfig(api_key="x", base_url="https://api.talonic.com/")
    assert cfg.base_url == "https://api.talonic.com"
