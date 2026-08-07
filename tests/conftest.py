import urllib.error
import urllib.request

import pytest


@pytest.fixture(autouse=True)
def no_real_network(monkeypatch):
    """
    Every test runs with no ANTHROPIC_API_KEY and no outbound network access,
    so tools that call external services (Voyage AI embeddings, Claude) are
    forced onto their local fallback paths. Individual tests can still
    monkeypatch things back on to exercise the "external call succeeds" path.
    """
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    def _blocked_urlopen(*args, **kwargs):
        raise urllib.error.URLError("network access is disabled in tests")

    monkeypatch.setattr(urllib.request, "urlopen", _blocked_urlopen)
