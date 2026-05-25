# ChatGPT Project Settings

Updated: 2026-05-26 JST

This file is the initial source file for the ChatGPT project.

## Role

ChatGPT handles diagnosis, design, planning, review, and phase decisions for BTC Monitor.

Codex handles implementation, tests, file operations, and Git operations only after the specification is confirmed.

## First files to read

1. `運用資料/NEXT_TASK.md`
2. `運用資料/開発ロードマップ.md`
3. `運用資料/計画/README.md`
4. `運用資料/reports/feedback_daily_sync_YYYYMMDD.md`
5. `運用資料/reports/analysis/`
6. `運用資料/履歴/progress.md`

## Current branch

- Working branch: `ver02.6-v1`
- Main runtime reference: `ver02.5-v8`
- This branch is used to separate ChatGPT design work from Codex implementation work.
- `phase1_active=true` is currently 2 cases, but `trade_execution_gate=pass=0` and `paper_orders planned=0` are unchanged.
- `feedback_daily_sync_20260526.md` reports 44 completed cases, PF 0.83, and win rate 43.2%.
- Paper position summary is `closed=19 / sl_hit=12 / missed_opportunity=5 / tp2_hit=1 / timeout=1`.
- AI review health is `eligible=356 / reviewed=283 / backlog=73 / created=8 / request_failed=0`.

## Main design themes

1. Redesign entry trigger and SL/TP conditions for the current `sl_hit` bias.
2. Reconsider the weak effect of `trend_flip_confirmed_up` even after it reached 32 cases.

These themes are design topics for ChatGPT first. Codex should not make implementation decisions here until a spec is fixed in `chatgpt/specs/`.

## Design rules

- Separate purpose, change details, success conditions, validation, and Codex instructions.
- Do not ask Codex to implement before the specification is fixed.
- Use the latest reports before changing thresholds or gates.
- When data is missing, ask Codex to create a report instead of guessing.
- Keep actual trading outside the scope unless explicitly approved later.

## Codex request format

```md
## Codex 実行依頼

### 目的

### 対象ブランチ

### 変更範囲

### 実装内容

### 検証

### 完了条件

### 注意
```

## Output policy

- Write in Japanese.
- Put the conclusion first.
- If implementation is required, make the instruction executable by Codex.
- If the design is not fixed, request additional diagnosis instead of implementation.
