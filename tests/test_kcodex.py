from __future__ import annotations

from pathlib import Path

import pytest

from core.config import ConfigBundle
from core.kcodex import KCodexError, KCodexWriter


def _schema_path() -> Path:
    return Path("schemas/k_codex.json")


@pytest.mark.skipif(not _schema_path().exists(), reason="Schema missing in test env.")
def test_build_and_write_kcodex(tmp_path: Path) -> None:
    writer = KCodexWriter(_schema_path())
    config = ConfigBundle(payload={"foo": "bar"}, sha256="abc123")
    record = writer.build_record(
        experiment="historical_k_v1",
        params={"years": [1800, 1810]},
        estimators={
            "phi": "historical_proxy",
            "te": {"estimator": "none", "k": 0, "lag": 0},
        },
        metrics={"K": 1.0},
        config=config,
        seed=42,
    )
    path = writer.write(record, tmp_path)
    assert path.exists()
