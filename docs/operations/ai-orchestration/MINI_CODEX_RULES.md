# MINI_CODEX_RULES

## Purpose

Codex 5.4-mini medium 向けの最小運用ルールです。

## Lightweight workflow

- ChatGPT が MCP で repo 確認、判断、対象 file 特定を担う
- Codex は local edit、最小 test、必要時 commit に集中する
- 同じ Codex thread 内では既知前提を繰り返さず、差分指示でよい
- `Read` / `Edit` / `Do not edit` の巨大リストは通常不要
- ただし `source` / `runtime` / `generated` / `logs` / `private` / `order` 系の危険境界は明示する

## Scope control

- task は 1 から 3 個の edit files を基本にする
- 5 個を超える edit files は明示的 authorization が必要
- broad repo exploration はしない
- missing required file があれば `BLOCKED`
- source / runtime / generated files は Edit に明示されたときだけ触る
- clean, archive, move, delete, refactor は明示要求がない限りしない

## Test and commit

- task で指定された最小限の check だけ実行する
- task に test がなければ追加しない
- commit は毎 task 必須ではない
- commit は `source/test変更`、`一区切りの docs 整理`、`人間に残すべき状態変更` のときだけ
- 小さな確認、数値 FIX、`NEXT_ACTION` だけの更新では原則 commit しない
- `TASK_LEDGER` / `CURRENT_HANDOFF` の逐次更新は通常不要で、大きな節目だけにする

## Safety boundary

- `CHECKPOINT_PUSH` 以外では push しない
- old runtime execution repo には触らない
- push / pull / runtime action が必要なら明示されていない限り止める
- product / trading / safety judgment が必要なら、task に rule が埋め込まれていない限り止める

## Report

- response.txt は必要最小限の compact report だけ
- 該当 file、test、commit、push を簡潔に書く

## Stop rule

- required file が missing なら `BLOCKED`
- judgment が必要なら、task に rule が埋め込まれていない限り `BLOCKED`
- broad repo inspection が必要なら `BLOCKED`
- product / trading / safety judgment が必要なら `BLOCKED`

## Good task examples

- `NEXT_ACTION.md` の current summary だけを更新する
- `PROMPTS.md` の 1 つの template を差し替える
- `REPO_MAP.md` に 1 行 anchor を足す

## Bad task examples

- repo 全体の再設計をする
- どの candidate を archive するかを Codex が判断する
- push 先を推測して実行する
- old runtime execution repo を勝手に触る
