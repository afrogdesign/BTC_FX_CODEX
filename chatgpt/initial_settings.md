# ChatGPT Project Settings

Updated: 2026-05-26 JST

This file is a short source file for the ChatGPT project.
The canonical settings live in `運用資料/ChatGPTプロジェクト設定.md`.
Latest instructions, current priorities, and the names of the latest reports always live in `運用資料/NEXT_TASK.md`.

## Role

ChatGPT handles diagnosis, design, planning, review, and phase decisions for BTC Monitor.
Codex handles implementation only after a confirmed spec exists in `chatgpt/specs/active/`.

## First files to read

1. `運用資料/ChatGPTプロジェクト設定.md`
2. `運用資料/NEXT_TASK.md`
3. `運用資料/開発ロードマップ.md`
4. `運用資料/reports/feedback_daily_sync_YYYYMMDD.md`
5. `運用資料/reports/analysis/`
6. `運用資料/履歴/progress.md`

## Current branch

- Working branch: `ver02.6-v1`
- Main runtime reference: `ver02.5-v8`
- This branch is used to separate ChatGPT design work from Codex implementation work.

## Main design themes

1. Redesign entry trigger and SL/TP conditions for the current `sl_hit` bias.
2. Reconsider the weak effect of `trend_flip_confirmed_up` even after it reached 32 cases.

## Operational rules

- Treat `運用資料/ChatGPTプロジェクト設定.md` as the source of truth for roles, reading order, and design rules.
- Treat `運用資料/NEXT_TASK.md` as the source of truth for current state, next tasks, and latest report references.
- Put unfinished thinking in `chatgpt/analysis/`.
- Put confirmed implementation specs in `chatgpt/specs/active/`.
- Move completed or historical specs to `chatgpt/specs/archive/`.
- Keep actual trading outside scope unless explicitly approved later.
