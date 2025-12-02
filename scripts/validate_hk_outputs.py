#!/usr/bin/env python3
from __future__ import annotations

"""
Validate Historical K pipeline outputs in logs/ for CI and local checks.

Checks:
  - logs/historical_k/k_t_series.csv has columns year,K and rows > 0
  - logs/regimes/regimes.csv has columns regime_id,start_year,end_year and rows > 0
  - logs/forecasting/forecast.json has years, forecast, ci_lower, ci_upper arrays with equal, non-zero length
"""

import json
from pathlib import Path
import sys

import pandas as pd


def fail(msg: str) -> None:
    print(f"❌ {msg}")
    sys.exit(1)


def ok(msg: str) -> None:
    print(f"✅ {msg}")


def validate_series(path: Path) -> None:
    if not path.exists():
        fail(f"Missing series CSV: {path}")
    df = pd.read_csv(path)
    if not {"year", "K"}.issubset(df.columns):
        fail(f"Series CSV missing required columns: {set(df.columns)}")
    if len(df) == 0:
        fail("Series CSV has no rows")
    # Basic bounds check (K expected between 0 and 2 in most configs; allow small margin)
    k = pd.to_numeric(df["K"], errors="coerce").dropna()
    if (k < -0.1).any() or (k > 2.5).any():
        fail("Series K values out of expected bounds [-0.1, 2.5]")
    ok(f"Series ok: {len(df)} rows (K in bounds)")


def validate_regimes(path: Path) -> None:
    if not path.exists():
        fail(f"Missing regimes CSV: {path}")
    df = pd.read_csv(path)
    req = {"regime_id", "start_year", "end_year"}
    if not req.issubset(df.columns):
        fail(f"Regimes CSV missing columns: need {req}, got {set(df.columns)}")
    if len(df) == 0:
        fail("Regimes CSV has no rows")
    # Numeric and temporal order checks
    df = df.copy()
    for col in ["regime_id", "start_year", "end_year"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    if df[["regime_id", "start_year", "end_year"]].isna().any().any():
        fail("Regimes CSV contains non-numeric values")
    if not (df["end_year"] >= df["start_year"]).all():
        fail("Regimes contain end_year < start_year")
    ok(f"Regimes ok: {len(df)} rows")


def validate_forecast(path: Path) -> None:
    if not path.exists():
        fail(f"Missing forecast JSON: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    keys = {"years", "forecast", "ci_lower", "ci_upper"}
    if not keys.issubset(data.keys()):
        fail(f"Forecast JSON missing keys: need {keys}, got {set(data.keys())}")
    n = len(data["years"])
    if not (n and n == len(data["forecast"]) == len(data["ci_lower"]) == len(data["ci_upper"])):
        fail("Forecast arrays lengths mismatch or zero")
    # Numeric checks
    for key in ("forecast", "ci_lower", "ci_upper"):
        vals = pd.Series(data[key]).astype(float)
        if vals.isna().any():
            fail(f"Forecast {key} contains non-numeric values")
    ok(f"Forecast ok: {n} steps to {data['years'][-1]}")


def main() -> None:
    logs = Path("logs")
    validate_series(logs / "historical_k" / "k_t_series.csv")
    validate_regimes(logs / "regimes" / "regimes.csv")
    validate_forecast(logs / "forecasting" / "forecast.json")
    ok("All HK outputs valid")


if __name__ == "__main__":
    main()
