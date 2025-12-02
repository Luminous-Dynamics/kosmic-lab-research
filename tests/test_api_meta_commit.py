from __future__ import annotations

from fastapi.testclient import TestClient

from historical_k.api import app


def test_meta_includes_git_commit() -> None:
    client = TestClient(app)
    r = client.get("/meta")
    assert r.status_code == 200
    body = r.json()
    cfg = body.get("config", {})
    assert "git_commit" in cfg
    assert isinstance(cfg.get("git_commit"), str)

