# BTCFX-20260608-039 monitor runtime code status

## 作業番号

- `BTCFX-20260608-039`

## 目的

- `BTCFX-20260608-038` 作業ログの commit hash placeholder を補正する。
- 監視サイクルがどの worktree / branch / commit / Python / main.py で動いているかを読み取り確認する。
- 監視プロセスの起動・停止・再起動は行わない。

## 確認対象

- LaunchAgent `com.afrog.btc-monitor`
- `~/Library/LaunchAgents/com.afrog.btc-monitor.plist`
- runtime worktree
- `main.py`
- `src/storage/csv_logger.py`
- `src/trade/active_plan.py`
- `logs/csv/trades.csv`
- `logs/csv/active_plan_candidates.csv`
- `logs/last_result.json`
- `logs/runtime/monitor.err`

## 確認結果

### LaunchAgent

- exists: `yes`
- state: `running`
- pid: `680`
- ProgramArguments: `["/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor/.venv312/bin/python", "-u", "/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor/main.py"]`
- WorkingDirectory: `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`
- StandardOutPath: `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor/logs/runtime/monitor.out`
- StandardErrorPath: `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor/logs/runtime/monitor.err`
- process start: `Sat Jun 6 16:24:40 2026`
- last exit code: `never exited`

### runtime worktree

- path: `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`
- exists: `yes`
- branch: `Ver03-v1`
- HEAD: `97c0c9b`
- status: `dirty`
- dirty summary:
  - untracked: `運用資料/計画/Ver03-v1_Codex再開引き継ぎ_20260608.md`
- latest commits:
  - `97c0c9b` Record Active Plan runtime status
  - `113e7c6` Add Active Plan runtime check runbook
  - `8d23f21` Resolve Ver03-v1 untracked files
  - `662da68` Document Ver03-v1 untracked files
  - `f75b40a` Sync Ver03-v1 next task tracker

### runtime code

- `main.py` has `build_active_trade_plan`: `yes`
- `main.py` has `append_active_plan_candidates`: `yes`
- `csv_logger.py` has `active_primary_action` column: `yes`
- `csv_logger.py` has `ACTIVE_PLAN_CANDIDATE_HEADER`: `yes`
- `csv_logger.py` has `append_active_plan_candidates`: `yes`
- `src/trade/active_plan.py` exists: `yes`

### runtime data

- `logs/heartbeat.txt`: `exists` / `2026-06-08 19:05:00 +0900`
- `logs/last_result.json`: `exists` / `2026-06-08 19:05:07 +0900`
- `logs/csv/trades.csv`: `exists`
- `logs/csv/active_plan_candidates.csv`: `missing`
- latest trades row summary:
  - data rows: `2077`
  - latest `signal_id`: `20260608_100500`
  - latest `timestamp_jst`: `2026-06-08T19:05:00.093581+09:00`
  - latest subject still includes: `[Ver02.6-v2]`
  - trades header `active_*`: `active_level_role` only
  - `active_plan_version` column: `no`
  - `active_primary_action` column: `no`
- last_result Active Plan:
  - `active_trade_plan present`: `no`
  - `active_primary_action`: `None`
  - `active_plan_version`: `None`
  - `trade_execution_gate`: `blocked`
  - `paper_order_status`: `""`

### runtime errors

- `logs/runtime/monitor.err`: `empty`
- error summary:
  - visible runtime error は確認されなかった

## 判断

- LaunchAgent の起動対象は `Ver03-v1` / `97c0c9b` / `.venv312/bin/python` / この worktree 自身だった。
- ただし監視 PID `680` は `2026-06-06 16:24:40` 起動のまま継続稼働しており、`97c0c9b` や 032 以降の変更を取り込む前の in-memory code が動き続けている可能性が高い。
- `main.py` と `csv_logger.py` には Active Plan 実装が存在する一方、runtime 出力の `trades.csv` header と `last_result.json` には Active Plan が反映されていないため、`候補条件未発生なだけ` では説明できない。

## 次にやること

- 次作業で安全に監視 worktree と実行中プロセスの同期状態を確認し、必要なら LaunchAgent 再起動手順を出す。
- 再起動判断までは、`active_plan_candidates.csv` 未生成を候補条件未発生だけで解釈しない。

## commit hash

- commit後に確定
