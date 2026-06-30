# CHECKPOINT_RUNBOOK

## Purpose

MCP primary ワークフローでの最小 checkpoint push 手順を定義します。
実行はしません。

## When to use CHECKPOINT_PUSH

- 意味のある branch checkpoint のときだけ使う
- `CHECKPOINT_PUSH` を task 本文に明示したときだけ使う

## When not to push

- 毎 task の routine push はしない
- branch の節目でないときは push しない
- old runtime execution repo を触る目的では使わない

## Preconditions

- task scope が checkpoint push を明示している
- local validation が完了している
- commit 対象が MCP working repo に限られている

## Required checks before checkpoint

- `git status --short --branch`
- `git diff --check`
- `git diff --name-only`
- staged 後の `git diff --cached --check`
- staged 後の `git diff --cached --name-only`
- staged 後の `git diff --cached --stat`

## Branch / remote rule

- push target は推測しない
- branch / remote / upstream が曖昧なら `BLOCKED`
- 明示された checkpoint 先だけを使う

## Push rule

- local checks が通ってからだけ push する
- generated files, secrets, runtime files, logs, `.venv312/`, unrelated files を含めない
- old runtime execution repo は触らない

## After push

- 実際の commit hash を compact report に書く
- push 結果と checkpoint 対象を簡潔に報告する
- 次の runtime pull handoff は別 task に分離する

## Stop conditions

- branch / remote / upstream が曖昧
- local checks が失敗
- scope 外の file が混入
- secrets や runtime files が見える
- old runtime execution repo を触る必要が出た

## Compact report fields

- `WORK_ID`
- `STATUS`
- `CHANGED`
- `TESTS`
- `COMMIT`
- `PUSH`
- `NOTES`
