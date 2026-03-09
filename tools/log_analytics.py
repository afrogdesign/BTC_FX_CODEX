from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


@dataclass
class Row:
    ts_jst: datetime
    raw: dict[str, str]


def _parse_dt(value: str) -> datetime | None:
    value = (value or "").strip()
    if not value:
        return None
    try:
        if value.endswith("Z"):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _split_values(value: str) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def _load_rows(csv_path: Path) -> list[Row]:
    if not csv_path.exists():
        return []

    rows: list[Row] = []
    with csv_path.open("r", encoding="utf-8", newline="") as fp:
        reader = csv.DictReader(fp)
        for raw in reader:
            dt = _parse_dt(raw.get("timestamp_jst", ""))
            if dt is None:
                dt_utc = _parse_dt(raw.get("timestamp_utc", ""))
                if dt_utc is None:
                    continue
                dt = dt_utc.astimezone(timezone.utc)
            rows.append(Row(ts_jst=dt, raw=raw))
    rows.sort(key=lambda r: r.ts_jst)
    return rows


def _filter_rows(rows: list[Row], year: int | None, month: str | None, date_from: str | None, date_to: str | None) -> list[Row]:
    filtered = rows

    if year is not None:
        filtered = [r for r in filtered if r.ts_jst.year == year]

    if month is not None:
        filtered = [r for r in filtered if r.ts_jst.strftime("%Y-%m") == month]

    if date_from:
        start = datetime.fromisoformat(date_from)
        filtered = [r for r in filtered if r.ts_jst.date() >= start.date()]

    if date_to:
        end = datetime.fromisoformat(date_to)
        filtered = [r for r in filtered if r.ts_jst.date() <= end.date()]

    return filtered


def _distribution(rows: list[Row], key: str) -> Counter[str]:
    c: Counter[str] = Counter()
    for r in rows:
        v = (r.raw.get(key, "") or "").strip() or "(empty)"
        c[v] += 1
    return c


def _ratio(numer: int, denom: int) -> float:
    if denom <= 0:
        return 0.0
    return numer / denom


def _fmt_pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def _bucket_summary(rows: list[Row], bucket: str) -> list[tuple[str, int, float, float, float]]:
    groups: dict[str, list[Row]] = defaultdict(list)
    for r in rows:
        if bucket == "year":
            key = str(r.ts_jst.year)
        else:
            key = r.ts_jst.strftime("%Y-%m")
        groups[key].append(r)

    out: list[tuple[str, int, float, float, float]] = []
    for key in sorted(groups.keys()):
        grp = groups[key]
        total = len(grp)
        conf = mean(_to_float(x.raw.get("confidence")) for x in grp)
        invalid = sum(1 for x in grp if (x.raw.get("primary_setup_status") or "") == "invalid")
        ai_error = sum(1 for x in grp if "ai_error" in _split_values(x.raw.get("reason_for_notification", "")))
        out.append((key, total, conf, _ratio(invalid, total), _ratio(ai_error, total)))
    return out


def _hourly_summary(rows: list[Row]) -> list[tuple[str, int, float, float]]:
    groups: dict[int, list[Row]] = defaultdict(list)
    for r in rows:
        groups[r.ts_jst.hour].append(r)

    out: list[tuple[str, int, float, float]] = []
    for hour in sorted(groups.keys()):
        grp = groups[hour]
        total = len(grp)
        conf = mean(_to_float(x.raw.get("confidence")) for x in grp)
        invalid = sum(1 for x in grp if (x.raw.get("primary_setup_status") or "") == "invalid")
        out.append((f"{hour:02d}:00", total, conf, _ratio(invalid, total)))
    return out


def _top_flags(rows: list[Row], limit: int = 10) -> list[tuple[str, int]]:
    c: Counter[str] = Counter()
    for r in rows:
        for flag in _split_values(r.raw.get("no_trade_flags", "")):
            c[flag] += 1
    return c.most_common(limit)


def _build_actions(total: int, invalid_rate: float, ai_error_rate: float, top_flags: list[tuple[str, int]]) -> list[str]:
    actions: list[str] = []
    if total < 50:
        actions.append("サンプル数が少ないため、まずは50件以上のログを蓄積してから閾値調整する。")
    if invalid_rate >= 0.7:
        actions.append("invalid比率が高い。`MIN_RR_RATIO` と `critical_zone` 周りの判定条件を優先レビューする。")
    if ai_error_rate >= 0.1:
        actions.append("AIエラー率が高い。`AI_TIMEOUT_SEC` と `AI_RETRY_COUNT` を見直し、API障害時の影響を下げる。")

    top1 = top_flags[0][0] if top_flags else ""
    if top1 == "RR_insufficient":
        actions.append("`RR_insufficient` が最多。S/R算出ロジックまたは `MIN_RR_RATIO` の妥当性を検証する。")
    if top1 == "Critical_zone_warning":
        actions.append("`Critical_zone_warning` が最多。ゾーン幅とATR係数を再調整して過剰警告を減らす。")

    if not actions:
        actions.append("大きな異常は見当たらない。現設定で継続し、月次で再評価する。")
    return actions


def _render_markdown(rows: list[Row], csv_path: Path, filters: dict[str, str]) -> str:
    if not rows:
        return "\n".join(
            [
                "# ログ分析レポート",
                "",
                f"- 対象CSV: `{csv_path}`",
                f"- 抽出条件: {filters}",
                "",
                "対象データが0件です。期間またはログ出力状態を確認してください。",
            ]
        )

    total = len(rows)
    start = rows[0].ts_jst.isoformat()
    end = rows[-1].ts_jst.isoformat()

    bias = _distribution(rows, "bias")
    phase = _distribution(rows, "phase")
    regime = _distribution(rows, "market_regime")
    setup = _distribution(rows, "primary_setup_status")

    confidences = [_to_float(r.raw.get("confidence")) for r in rows]
    avg_conf = mean(confidences)
    high_conf = sum(1 for v in confidences if v >= 80)
    invalid_count = setup.get("invalid", 0)
    ai_error_count = sum(1 for r in rows if "ai_error" in _split_values(r.raw.get("reason_for_notification", "")))

    yearly = _bucket_summary(rows, "year")
    monthly = _bucket_summary(rows, "month")
    hourly = _hourly_summary(rows)
    flags = _top_flags(rows, limit=10)

    actions = _build_actions(
        total=total,
        invalid_rate=_ratio(invalid_count, total),
        ai_error_rate=_ratio(ai_error_count, total),
        top_flags=flags,
    )

    lines: list[str] = []
    lines.append("# ログ分析レポート")
    lines.append("")
    lines.append("## 1. 集計条件")
    lines.append(f"- 対象CSV: `{csv_path}`")
    lines.append(f"- 抽出条件: {filters}")
    lines.append(f"- 対象期間: {start} 〜 {end}")
    lines.append(f"- 件数: {total}")
    lines.append("")

    lines.append("## 2. 全体KPI")
    lines.append(f"- 平均 confidence: `{avg_conf:.2f}`")
    lines.append(f"- high confidence (>=80): `{high_conf}` 件 ({_fmt_pct(_ratio(high_conf, total))})")
    lines.append(f"- primary_setup_status=invalid: `{invalid_count}` 件 ({_fmt_pct(_ratio(invalid_count, total))})")
    lines.append(f"- ai_error 発生: `{ai_error_count}` 件 ({_fmt_pct(_ratio(ai_error_count, total))})")
    lines.append("")

    lines.append("## 3. 分布")
    lines.append("### bias")
    for k, v in bias.most_common():
        lines.append(f"- {k}: {v}")
    lines.append("### phase")
    for k, v in phase.most_common():
        lines.append(f"- {k}: {v}")
    lines.append("### market_regime")
    for k, v in regime.most_common():
        lines.append(f"- {k}: {v}")
    lines.append("### primary_setup_status")
    for k, v in setup.most_common():
        lines.append(f"- {k}: {v}")
    lines.append("")

    lines.append("## 4. no_trade_flags 上位")
    if flags:
        for name, cnt in flags:
            lines.append(f"- {name}: {cnt}")
    else:
        lines.append("- no_trade_flags は記録なし")
    lines.append("")

    lines.append("## 5. 年次集計")
    lines.append("| year | count | avg_conf | invalid_rate | ai_error_rate |")
    lines.append("|---|---:|---:|---:|---:|")
    for y, c, conf, inv_r, ai_r in yearly:
        lines.append(f"| {y} | {c} | {conf:.2f} | {_fmt_pct(inv_r)} | {_fmt_pct(ai_r)} |")
    lines.append("")

    lines.append("## 6. 月次集計")
    lines.append("| month | count | avg_conf | invalid_rate | ai_error_rate |")
    lines.append("|---|---:|---:|---:|---:|")
    for m, c, conf, inv_r, ai_r in monthly:
        lines.append(f"| {m} | {c} | {conf:.2f} | {_fmt_pct(inv_r)} | {_fmt_pct(ai_r)} |")
    lines.append("")

    lines.append("## 7. 時間帯別（JST）")
    lines.append("| hour | count | avg_conf | invalid_rate |")
    lines.append("|---|---:|---:|---:|")
    for hour, c, conf, inv_r in hourly:
        lines.append(f"| {hour} | {c} | {conf:.2f} | {_fmt_pct(inv_r)} |")
    lines.append("")

    lines.append("## 8. 改善アクション候補")
    for idx, item in enumerate(actions, start=1):
        lines.append(f"{idx}. {item}")
    lines.append("")

    lines.append("## 9. 制約")
    lines.append("- このログには実トレード損益（PnL）がないため、勝率や期待値の厳密検証は不可。")
    lines.append("- 将来は約定結果（entry/exit/pnl）を記録すると、改善精度が大きく上がる。")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="BTC monitor logs/csv/trades.csv の分析レポートを作成")
    parser.add_argument("--csv", default="logs/csv/trades.csv", help="対象CSVパス")
    parser.add_argument("--year", type=int, default=None, help="対象年 (例: 2026)")
    parser.add_argument("--month", default=None, help="対象月 (例: 2026-03)")
    parser.add_argument("--from", dest="date_from", default=None, help="開始日 (YYYY-MM-DD)")
    parser.add_argument("--to", dest="date_to", default=None, help="終了日 (YYYY-MM-DD)")
    parser.add_argument("--output-md", default=None, help="出力Markdownパス")
    args = parser.parse_args()

    csv_path = Path(args.csv)
    rows = _load_rows(csv_path)
    filtered = _filter_rows(rows, args.year, args.month, args.date_from, args.date_to)

    filters = {
        "year": str(args.year) if args.year is not None else "all",
        "month": args.month or "all",
        "from": args.date_from or "none",
        "to": args.date_to or "none",
    }
    report = _render_markdown(filtered, csv_path, filters)

    if args.output_md:
        out_path = Path(args.output_md)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report, encoding="utf-8")
        print(f"saved: {out_path}")
    else:
        print(report)


if __name__ == "__main__":
    main()
