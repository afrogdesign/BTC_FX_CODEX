# P8 Daily Operating Cycle Automation — Active Specification

## Metadata

- work_id: `BTCFX-20260711-P8-DAILY-CYCLE-AUTOMATION`
- status: active / bounded implementation
- phase: P8 operating evidence collection
- runner: `run-p8-operating-cycle`
- schedule: daily 11:30 JST (`Asia/Tokyo`)
- launchd label: `com.afrog.btc-p8-operating-cycle`
- safety: report-only / not FORMAL_GO / no automatic order / human decides manually

## Purpose

Run one accepted P8 evidence cycle each day without manual lineage reconstruction. The wrapper only resolves the JST date, validates optional actual-evidence pairing, calls the accepted runner once, and writes a compact atomic last-result status. It does not reimplement P4/P5/P8 logic or apply tuning.

## CLI contract

`tools/run_p8_daily_cycle.py` accepts `--date YYYYMMDD` and `--dry-run` plus test-only path overrides. It invokes `tools/log_feedback.py run-p8-operating-cycle` with current candidates, `trades.csv`, explicit public OHLCV fetch, date output root `logs/p8_operating_cycles/YYYYMMDD/`, `--replace-output`, and `--stdout-json`, using an argv list and no shell string.

## Inputs and outputs

Default inputs are `logs/csv/active_plan_candidates.csv`, `logs/csv/trades.csv`, and the public OHLCV route. The runner's date-specific outputs are retained beneath the date directory. The wrapper writes only `logs/runtime/p8_daily_cycle_last_result.json` as compact status plus the fixed launchd stdout/stderr paths. Status contains JST timestamps, report date, success/failed/actual_pair_incomplete, return code, relative output/manifest/summary paths, safe counts/readiness/error codes, and the safety boundary. Raw rows, candles, notes, private paths, and secrets are excluded.

## Actual evidence pair

`logs/csv/manual_trade_episodes.csv` and `logs/csv/manual_trade_signal_links.csv` are passed together only when both exist. A single file is fail-closed as `actual_pair_incomplete` without starting the runner. When both are absent, the cycle runs normally as proxy-only evidence.

## Schedule and rerun

`deploy/com.afrog.btc-p8-operating-cycle.plist` declares the canonical primary repo, `.venv312/bin/python`, `WorkingDirectory`, `StartCalendarInterval` Hour 11 / Minute 30, fixed stdout/stderr paths, no RunAtLoad, and no KeepAlive. Same-day reruns use the same date directory and the runner's atomic `--replace-output` behavior. Installation, bootstrap, and runtime execution are a separate explicit runtime task.

## Failure and dry-run behavior

Expected runner failures write a compact failed last-result and return nonzero. Pair incompleteness writes a compact status and does not invoke the runner. Dry-run prints the argv contract only and writes neither outputs nor last-result. Temporary status files are atomically replaced and removed.

## Acceptance and archive condition

Targeted wrapper/runner tests, plist lint, and a wrapper dry-run must pass. Generated evidence remains local and uncommitted. This spec may be archived only after a separate runtime apply and first scheduled-cycle confirmation; this implementation task does not install or bootstrap launchd.

## Safety boundary

No classifier, gate, threshold, scoring, notification, mail, runtime, API, account, private endpoint, order behavior, automatic tuning, P9 activation, raw export, or `paper_positions.csv` integration is permitted.
