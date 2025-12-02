"""Debug script to understand cross-validation issue."""

from pathlib import Path

import numpy as np
import pandas as pd

# Load data
data_path = Path("logs/historical_k_extended/k_t_series_5000y.csv")
df = pd.read_csv(data_path)

print("=== Data Overview ===")
print(f"Total rows: {len(df)}")
print(f"Columns: {df.columns.tolist()}")
print(f"\nFirst few rows:")
print(df.head())
print(f"\nLast few rows:")
print(df.tail())

# Extract K series and harmonies
k_series = pd.Series(df["K"].values, index=df["year"].values)
harmony_cols = [c for c in df.columns if c not in ["year", "K", "K_lower", "K_upper"]]
harmony_frame = df[harmony_cols]

print(f"\n=== K Series ===")
print(f"Length: {len(k_series)}")
print(
    f"Min: {k_series.min():.4f}, Max: {k_series.max():.4f}, Mean: {k_series.mean():.4f}"
)
print(f"Std: {k_series.std():.4f}")
print(f"Any NaN? {k_series.isna().any()}")

print(f"\n=== Harmony Frame ===")
print(f"Shape: {harmony_frame.shape}")
print(f"Columns: {harmony_cols}")
print(f"Any NaN? {harmony_frame.isna().any().any()}")

# Test one fold
n_folds = 5
n_years = len(k_series)
fold_size = n_years // n_folds

print(f"\n=== Testing Fold 1 ===")
i = 0
test_indices = list(range(i * fold_size, min((i + 1) * fold_size, n_years)))
print(
    f"Test indices: {len(test_indices)} rows (indices {test_indices[0]} to {test_indices[-1]})"
)

test_mask = np.zeros(n_years, dtype=bool)
test_mask[test_indices] = True
train_mask = ~test_mask

train_frame = harmony_frame[train_mask]
test_frame = harmony_frame[test_mask]
k_train = k_series[train_mask]
k_test = k_series[test_mask]

print(f"Train: {len(k_train)} rows")
print(f"Test: {len(k_test)} rows")

# Compute prediction
k_pred = test_frame.mean(axis=1)

print(f"\n=== Predictions ===")
print(f"k_pred length: {len(k_pred)}")
print(
    f"k_pred min: {k_pred.min():.4f}, max: {k_pred.max():.4f}, mean: {k_pred.mean():.4f}"
)
print(f"k_pred std: {k_pred.std():.4f}")
print(f"k_pred any NaN? {k_pred.isna().any()}")

print(f"\n=== Actual Test Values ===")
print(f"k_test length: {len(k_test)}")
print(
    f"k_test min: {k_test.min():.4f}, max: {k_test.max():.4f}, mean: {k_test.mean():.4f}"
)
print(f"k_test std: {k_test.std():.4f}")
print(f"k_test any NaN? {k_test.isna().any()}")

# Check if indices match
print(f"\n=== Index Alignment ===")
print(f"k_pred index: {k_pred.index[:5].tolist()}...")
print(f"k_test index: {k_test.index[:5].tolist()}...")
print(f"Indices equal? {k_pred.index.equals(k_test.index)}")

# Try to compute metrics
print(f"\n=== Computing Metrics ===")
diff = k_pred - k_test
print(f"k_pred - k_test:")
print(f"  Any NaN? {diff.isna().any()}")
print(f"  Values: {diff.describe()}")

squared_diff = (k_pred - k_test) ** 2
print(f"\n(k_pred - k_test)^2:")
print(f"  Any NaN? {squared_diff.isna().any()}")
print(f"  Mean: {squared_diff.mean()}")

rmse = float(np.sqrt(squared_diff.mean()))
mae = float(np.abs(diff).mean())

print(f"\n=== Final Metrics ===")
print(f"RMSE: {rmse}")
print(f"MAE: {mae}")
print(f"RMSE is NaN? {np.isnan(rmse)}")
print(f"MAE is NaN? {np.isnan(mae)}")
