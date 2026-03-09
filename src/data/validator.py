from __future__ import annotations

import pandas as pd


def validate_klines(df: pd.DataFrame, min_rows: int) -> bool:
    if df is None or df.empty:
        return False
    required_cols = {"timestamp", "open", "high", "low", "close", "volume"}
    if not required_cols.issubset(df.columns):
        return False
    if len(df) < min_rows:
        return False
    if df[list(required_cols)].isna().any().any():
        return False
    ts = df["timestamp"]
    if not ts.is_monotonic_increasing:
        return False
    if ts.duplicated().any():
        return False
    if (df["high"] < df["low"]).any():
        return False
    return True
