# PROMPT_PREFLIGHT_CHECKLIST

## Purpose

ChatGPT が Codex prompt を出す前に、形が崩れていないかを確認する。

## Required prompt fields

- Work ID
- Goal
- Working directory
- Codex model constraint
- Read
- Edit
- Do not edit
- Required changes
- Tests
- Stop
- Commit
- Report
- response.txt rules

## Size check

- 1 から 3 edit files を優先する
- 5 個を超える edit files は explicit authorization が必要
- broad repo inspection はしない
- scope が不明なら `AUTO_SEND` を出さない
- Codex judgment が必要なら、送る前に ChatGPT 側で決める

## Read/Edit boundary check

- Read は task に必要な file だけにする
- Edit は明示された file だけにする
- source, runtime, generated file は Edit に明示されている場合だけ触る

## Push/Pull check

- normal task は `Do not push` を明記する
- push は `CHECKPOINT_PUSH` だけで許可する
- pull は `RUNTIME_PULL_HANDOFF` だけで許可する
- push/pull target が曖昧なら `HUMAN_CHECK` か block

## Runtime repo check

- old runtime execution repo は通常 task で触らない
- `RUNTIME_PULL_HANDOFF` 以外では触らない

## Safety check

- product / trading / safety judgment が残っていないか確認する
- judgment が残るなら、送る前に ChatGPT が解決する
- unresolved なら `HUMAN_CHECK`

## Mini Codex check

- Codex 5.4-mini medium 向けには小さい task にする
- 機械的な edit を優先する
- broad exploration を避ける

## Stop / HUMAN_CHECK triggers

- required field が missing
- task scope が unclear
- push / pull / runtime repo が unresolved
- product judgment が unresolved
- safety judgment が unresolved
- task が oversized

## AUTO_SEND allowed conditions

- Goal が fixed
- Read files が fixed
- Edit files が fixed
- Required changes が explicit
- Tests が explicit
- Stop conditions が explicit
- push / pull / runtime behavior が explicit
- product / trading / safety decision が残っていない
- Codex が mechanical に完了できる

## Final output checklist

- task が malformed でない
- task が oversized でない
- push / pull / runtime repo が明確
- HUMAN_CHECK が必要なら先に止める
- AUTO_SEND 条件を満たすときだけ送る
