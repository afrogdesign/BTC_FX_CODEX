from __future__ import annotations

from typing import Any

import pandas as pd


def detect_swings(df: pd.DataFrame, n: int) -> dict[str, list[dict[str, Any]]]:
    highs: list[dict[str, Any]] = []
    lows: list[dict[str, Any]] = []
    if len(df) < n * 2 + 1:
        return {"highs": highs, "lows": lows}

    highs_col = df["high"].to_list()
    lows_col = df["low"].to_list()
    ts_col = df["timestamp"].to_list()

    for i in range(n, len(df) - n):
        left_h = highs_col[i - n : i]
        right_h = highs_col[i + 1 : i + 1 + n]
        left_l = lows_col[i - n : i]
        right_l = lows_col[i + 1 : i + 1 + n]
        cur_h = highs_col[i]
        cur_l = lows_col[i]

        if cur_h >= max(left_h) and cur_h >= max(right_h):
            highs.append({"idx": i, "timestamp": int(ts_col[i]), "price": float(cur_h)})
        if cur_l <= min(left_l) and cur_l <= min(right_l):
            lows.append({"idx": i, "timestamp": int(ts_col[i]), "price": float(cur_l)})

    return {"highs": highs, "lows": lows}


def classify_structure(swings: dict[str, list[dict[str, Any]]]) -> str:
    highs = swings.get("highs", [])
    lows = swings.get("lows", [])
    if len(highs) < 2 or len(lows) < 2:
        return "mixed"

    prev_h, last_h = highs[-2], highs[-1]
    prev_l, last_l = lows[-2], lows[-1]

    hh = last_h["price"] > prev_h["price"]
    hl = last_l["price"] > prev_l["price"]
    lh = last_h["price"] < prev_h["price"]
    ll = last_l["price"] < prev_l["price"]

    if hh and hl:
        return "hh_hl"
    if lh and ll:
        return "lh_ll"
    return "mixed"


def calc_tf_signal(ema_alignment: str, structure: str) -> str:
    if ema_alignment == "bullish" and structure == "hh_hl":
        return "long"
    if ema_alignment == "bearish" and structure == "lh_ll":
        return "short"
    return "wait"
