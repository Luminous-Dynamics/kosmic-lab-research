#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from historical_k.api import app


def main() -> None:
    parser = argparse.ArgumentParser(description="Dump FastAPI OpenAPI schema to a file")
    parser.add_argument("--out", type=Path, default=Path("logs/openapi.json"))
    args = parser.parse_args()
    spec = app.openapi()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(spec, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"✅ OpenAPI schema written to {args.out}")


if __name__ == "__main__":
    main()

