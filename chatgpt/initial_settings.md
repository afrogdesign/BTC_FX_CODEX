# ChatGPT Project Settings

Updated: 2026-05-26 JST

This file is a short source file for the ChatGPT project.
The canonical settings live in `運用資料/ChatGPTプロジェクト設定.md`.
Latest instructions, current priorities, and the names of the latest reports always live in `運用資料/NEXT_TASK.md`.
The report routing hub always lives in `運用資料/reports/report_hub_latest.md`.

## Role

ChatGPT handles diagnosis, design, planning, review, and phase decisions for BTC Monitor.
Codex handles implementation only after a confirmed spec exists in `chatgpt/specs/active/`.

## First files to read

1. `運用資料/ChatGPTプロジェクト設定.md`
2. `運用資料/NEXT_TASK.md`
3. `運用資料/reports/report_hub_latest.md`
4. Hub から必要な raw report
5. `chatgpt/README.md`
6. 関連する `chatgpt/analysis/*.md`
7. 必要時だけ `運用資料/開発ロードマップ.md` と `運用資料/履歴/progress.md`

## Branch handling

- The latest working branch must always be read from `運用資料/NEXT_TASK.md`.
- When a new branch is created, `運用資料/NEXT_TASK.md` must be updated in the same work unit.
- Main runtime reference may differ from the current working branch.

## Main design themes

1. Redesign entry trigger and SL/TP conditions for the current `sl_hit` bias.
2. Reconsider the weak effect of `trend_flip_confirmed_up` even after it reached 32 cases.

## Operational rules

- Treat `運用資料/ChatGPTプロジェクト設定.md` as the source of truth for roles, reading order, and design rules.
- Treat `運用資料/NEXT_TASK.md` as the source of truth for current state, next tasks, and latest report references.
- Treat `運用資料/reports/report_hub_latest.md` as the routing index for raw reports.
- Put unfinished thinking and current design continuity notes in `chatgpt/analysis/`.
- Put confirmed implementation specs in `chatgpt/specs/active/`.
- Move completed or historical specs to `chatgpt/specs/archive/`.
- Keep actual trading outside scope unless explicitly approved later.
