from __future__ import annotations

import json
from pathlib import Path

from scripts import checkpoint_tool, config_registry


def test_config_registry_cli(tmp_path, monkeypatch) -> None:
    # Redirect registry path
    reg_path = tmp_path / "registry.json"
    monkeypatch.setattr(config_registry, "REGISTRY_PATH", reg_path)

    # Create two simple configs
    cfg_a = tmp_path / "a.yaml"
    cfg_b = tmp_path / "b.yaml"
    cfg_a.write_text("alpha: 1\nbeta: 2\n", encoding="utf-8")
    cfg_b.write_text("alpha: 1\nbeta: 3\n", encoding="utf-8")

    # Register config A
    entry = config_registry.register_config(cfg_a, "Test A", notes=None)
    assert entry["label"] == "Test A"
    assert reg_path.exists()

    # Lookup by path and by hash
    looked = config_registry.lookup(config_path=cfg_a)
    assert looked and looked["path"].endswith("a.yaml")
    looked2 = config_registry.lookup(hash_value=looked["hash"])
    assert looked2 and looked2["hash"] == looked["hash"]

    # Diff shows beta change
    diff = config_registry.diff_configs(cfg_a, cfg_b)
    assert "-beta: 2" in diff and "+beta: 3" in diff


def test_checkpoint_tool_cli(tmp_path, monkeypatch) -> None:
    # Create minimal checkpoint with embedded config snapshot
    ckpt = tmp_path / "ckpt.json"
    snapshot = "alpha: 1\nbeta: 2\n"
    payload = {
        "agent_class": "SimpleAgent",
        "phase": "G2",
        "saved_at": "2025-11-22T12:00:00Z",
        "state": {},
        "metadata": {
            "config": {"path": "dummy", "sha256": "deadbeef"},
            "config_snapshot": snapshot,
        },
    }
    ckpt.write_text(json.dumps(payload), encoding="utf-8")

    # info
    checkpoint_tool.main(["info", "--path", str(ckpt)])

    # list
    dir_path = tmp_path / "ckpts"
    dir_path.mkdir()
    (dir_path / "a.json").write_text(json.dumps(payload), encoding="utf-8")
    checkpoint_tool.main(["list", "--dir", str(dir_path)])

    # copy
    dest = tmp_path / "ckpt_copy.json"
    checkpoint_tool.main(
        ["copy", "--src", str(ckpt), "--dest", str(dest), "--overwrite"]
    )
    assert dest.exists()

    # extract-config
    out_yaml = tmp_path / "config.yaml"
    checkpoint_tool.main(
        ["extract-config", "--path", str(ckpt), "--output", str(out_yaml)]
    )
    assert out_yaml.read_text(encoding="utf-8") == snapshot
