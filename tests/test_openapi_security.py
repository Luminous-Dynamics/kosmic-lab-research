from __future__ import annotations

import importlib
import sys


def test_openapi_security_schemes_present(monkeypatch) -> None:
    # With token configured, security schemes should be present and applied
    monkeypatch.setenv("KOSMIC_API_TOKEN", "secret")
    if "historical_k.api" in sys.modules:
        del sys.modules["historical_k.api"]
    import historical_k.api as api  # type: ignore
    importlib.reload(api)

    spec = api.app.openapi()
    schemes = spec.get("components", {}).get("securitySchemes", {})
    assert "HTTPBearer" in schemes and "ApiKeyAuth" in schemes

    # Public paths should have empty security; others should require auth
    assert spec["paths"]["/health"]["get"].get("security") == []
    # Artifacts path should require one of the security schemes
    sec = spec["paths"]["/k/series"]["get"].get("security")
    assert isinstance(sec, list) and any("HTTPBearer" in x or "ApiKeyAuth" in x for x in sec)

