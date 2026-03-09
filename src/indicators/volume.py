from __future__ import annotations

import pandas as pd


def calculate_volume_ratio(volume: pd.Series, lookback: int = 20) -> pd.Series:
    avg = volume.rolling(window=lookback, min_periods=1).mean()
    ratio = volume / avg.replace(0, pd.NA)
    return ratio.fillna(1.0)
