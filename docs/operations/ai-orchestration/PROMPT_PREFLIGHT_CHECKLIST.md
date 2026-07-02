# PROMPT_PREFLIGHT_CHECKLIST

## Purpose

ChatGPT が Codex prompt を出す前に、形と境界が崩れていないかを確認する。

## Required prompt fields

- Work ID
- Goal
- Allowed read
- Allowed edit
- Allowed inspection
- Do
- Validation
- Stop
- Commit
- Report

旧来の長い safety boilerplate は毎回フル記載しない。危険境界に関係するものだけを書く。

## BOUNDED_CODEX preflight

- fixed-scope source / test / docs work なら `BOUNDED_CODEX` を第一候補にする
- ChatGPT が product / safety / scope を先に固定する
- Codex に broad exploration をさせない
- review-only なら `REVIEW_ONLY`、極小修正なら `LIGHT_CODEX` を検討する

## Size check

- 1 から 3 edit files を優先する
- 5 個を超える edit files は explicit authorization が必要
- scope が不明なら送らない
- Codex judgment が必要なら、送る前に ChatGPT 側で決める

## Read/Edit/Inspection boundary check

- Allowed read は task に必要な file だけにする
- Allowed edit は明示された file だけにする
- Allowed inspection は current diff/status、nearby helpers、matching tests など task に必要な最小限に絞る
- source、runtime、generated file は Edit に明示されている場合だけ触る

## Docs update check

- docs を Allowed edit に足す前に、runtime / deployment / rollback / launchd / mail sending / safety boundary / handoff の作業かを確認する
- next operator action が実際に変わるかを確認する
- `CURRENT_STATE.md` が milestone 変更のために本当に必要かを確認する
- すべて no なら docs files を入れない
- UI / source / test fixes は原則 docs update なしにする

## Push/Pull check

- normal task は `Do not push` を明記する
- push は `CHECKPOINT_PUSH` だけで許可する
- pull は `RUNTIME_PULL_HANDOFF` だけで許可する
- push/pull target が曖昧なら止める

## Runtime repo check

- old runtime execution repo は通常 task で触らない
- `RUNTIME_PULL_HANDOFF` 以外では触らない

## Safety check

- product / trading / safety judgment が残っていないか確認する
- runtime judgment が残っていないか確認する
- unresolved judgment があるなら、送る前に ChatGPT が解決する
- full safety boilerplate は避ける
- current task に関係する safety stop だけを書く

## HUMAN_CHECK triggers

- required field が missing
- task scope が unclear
- push / pull / runtime repo が unresolved
- product judgment が unresolved
- safety judgment が unresolved
- runtime judgment が unresolved
- task が oversized

## Final output checklist

- task が malformed でない
- task が oversized でない
- push / pull / runtime repo が明確
- HUMAN_CHECK が必要なら先に止める
