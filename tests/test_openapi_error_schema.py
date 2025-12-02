from __future__ import annotations

from historical_k.api import app


def test_openapi_includes_error_model_for_404() -> None:
    spec = app.openapi()
    # Error model present
    schemas = spec.get("components", {}).get("schemas", {})
    assert "ErrorModel" in schemas
    # Check a few endpoints have 404 response referencing the schema
    paths = spec.get("paths", {})
    for p in ("/k/series", "/k/summary", "/k/plot", "/regimes", "/forecast"):
        for code in ("401", "404", "429"):
            resp = paths[p]["get"].get("responses", {}).get(code, {})
            assert "content" in resp
            appjson = resp["content"].get("application/json", {})
            schema = appjson.get("schema", {})
            # Expect a $ref to ErrorModel
            ref = schema.get("$ref", "")
            assert ref.endswith("/ErrorModel"), f"{code} schema for {p} did not reference ErrorModel"
