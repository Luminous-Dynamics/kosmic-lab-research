#!/usr/bin/env python3
"""
Prune large/generated directories to keep working trees lean.

Defaults to dry-run; pass --apply to actually delete.
Examples:
  poetry run python scripts/prune_artifacts.py
  poetry run python scripts/prune_artifacts.py --apply --keep-days 14
"""
from __future__ import annotations

import argparse
import shutil
import time
import subprocess
from pathlib import Path
from typing import Iterable


DEFAULT_TARGETS = [
    "logs",
    "results",
    "artifacts",
    "archives",
    "figures",
    "figs",
    "tmp_logs_test",
    "htmlcov",
]


def prune_path(path: Path, *, apply: bool, keep_days: int) -> None:
    if not path.exists():
        return
    if _is_tracked(path):
        print(f"⏭️  Skipping tracked path {path}")
        return
    now = time.time()
    cutoff = now - keep_days * 86400
    age_ok = True
    try:
        mtime = path.stat().st_mtime
        age_ok = mtime < cutoff
    except OSError:
        pass
    if not age_ok:
        return
    if apply:
        print(f"🗑️  Removing {path}")
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        else:
            path.unlink(missing_ok=True)
    else:
        print(f"[dry-run] would remove {path}")


def iter_targets(targets: Iterable[str]) -> Iterable[Path]:
    for t in targets:
        yield Path(t)


def _is_tracked(path: Path) -> bool:
    """Best-effort check if a file/dir is tracked by git; skip if so."""
    try:
        if path.is_dir():
            result = subprocess.run(
                ["git", "ls-files", str(path)],
                capture_output=True,
                text=True,
                check=False,
            )
            return bool(result.stdout.strip())
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", str(path)],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0
    except Exception:
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Prune generated artifacts")
    parser.add_argument(
        "--targets",
        nargs="*",
        default=DEFAULT_TARGETS,
        help="Directories/files to prune",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually delete paths (default: dry-run)",
    )
    parser.add_argument(
        "--keep-days",
        type=int,
        default=30,
        help="Keep items newer than this many days",
    )
    args = parser.parse_args()

    for target in iter_targets(args.targets):
        prune_path(target, apply=args.apply, keep_days=args.keep_days)


if __name__ == "__main__":
    main()
