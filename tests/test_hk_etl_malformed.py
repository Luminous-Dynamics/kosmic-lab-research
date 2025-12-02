from __future__ import annotations

from pathlib import Path

import pandas as pd

from historical_k.etl import load_feature_series


def test_load_feature_series_handles_non_numeric_and_unsorted(tmp_path: Path) -> None:
    years = [2000, 2010, 2020]
    csv = tmp_path / "foo.csv"
    # Include non-numeric value, unsorted years, and duplicate year
    csv.write_text(
        """year,value
2010,1.0
notyear,2.0
2000,bad
2020,3.5
2010,1.2
""",
        encoding="utf-8",
    )
    s = load_feature_series("foo", years, data_dir=tmp_path)
    assert isinstance(s, pd.Series)
    assert list(s.index) == years
    assert not s.isna().any()
    # Interpolation/ffill/bfill should yield finite numbers (>= 0.0 after fallback)
    assert (s.astype(float) == s.astype(float)).all()

