# AI Orchestration Control

last_updated: 2026-07-21

このファイルは変化しにくい運用規則だけを保持する。現在のphaseやWork IDは `CURRENT_STATE.md` と `NEXT_ACTION.md` を正本とする。

## Repo boundary

| Label | Path | Rule |
|---|---|---|
| primary working repo | `/Users/marupro/CODEX/100_MCP_Server/btc_monitor` | 通常のread、edit、test、git |
| frozen old runtime repo | `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor` | 明示されたruntime task以外ではread/edit/runしない |

- branchは `git status --short --branch` で確認する。
- chat historyや古い文書のbranch値を固定値として使わない。
- ChatGPTは `AFROG_Business_MCP` でrepo実体を先に確認する。

## Roles

### ChatGPT

- repo inspection
- product / trading / safety判断
- scope固定
- active spec作成・修正
- 対象fileとvalidationの特定
- Codex prompt作成
- Codex結果のrepo実体レビュー
- acceptanceと次作業の選択

### Codex

- 指定fileの限定inspectionと編集
- nearby helperとmatching testの確認
- task-specific validation
- local commit
- 明示されたcheckpoint push
- compact report

Codexにproduct判断、broad exploration、次phase選択、曖昧な仕様補完をさせない。

## Operation mode

- default: `BOUNDED_CODEX`
- review only: `REVIEW_ONLY`
- checkpoint push: `CHECKPOINT_PUSH`
- approved runtime operation: `RUNTIME_TASK`

通常task:

```text
status once
→ bounded edit
→ targeted validation
→ task-scoped diff check
→ allowed filesだけstage
→ local commit
→ compact report
```

pushは明示されたcheckpointだけで行う。

## Active spec

- source実装前に `chatgpt/specs/active/` を確認する。
- active specは実装の詳細正本。
- active specが空なら、未承認source実装を開始しない。
- route・安全境界と矛盾する場合はspec correctionへ戻す。
- archiveはChatGPT acceptance後だけ行う。

## Dirty tree

- dirtyだけを理由に停止しない。
- task対象と重なる差分は内容を確認する。
- 対象外で独立した差分は変更・stage・commitしない。
- 由来不明で衝突可能なら停止する。
- reset、restore、checkout、clean、stash apply/pop/dropを行わない。
- commit時はtask対象fileだけを明示的にstageする。

## Validation

- docs-only: task-scoped `git diff --check`
- Python: matching unittest
- CLI/report: actual bounded command 1回とmatching unittest
- deterministic output contractがある場合だけrepeat runとbyte comparison
- full suiteは共有基盤変更または明示要求時のみ
- 同じ証拠を得る重複validationを避ける

## Safety boundary

- report-only
- not `FORMAL_GO`
- human-decided
- no automatic order
- no API keys、secrets、private/account/order endpoints
- no unapproved runtime restart、launchd、mail、notification behavior change
- no raw exchange export commit
- no unapproved `paper_positions.csv` integration
- no automatic production mutation

Human approvalなしで変更しない:

- `trade_execution_gate`
- `phase1b_lite_gate`
- `opportunity_gate`
- scoring、threshold、classifier
- notification trigger、real mail sending
- runtime schedule
- live order、API、secret

## Record discipline

- `CURRENT_STATE.md`: accepted stateとactive blockerだけ
- `NEXT_ACTION.md`: 現在の1 taskだけ
- `CONTROL.md`: stable ruleだけ
- `MILESTONES.md`: accepted major checkpointだけ
- `TASK_LEDGER.md`: historical search only
- active FIXの詳細はactive specへ短いfactual noteとして記録する
- commit/testの詳細はgitとcompact reportを正本にする
- 同じ事実を複数current fileへ重複記録しない

## Codex report handoff

Codexにlocal filesystem accessがあるtaskでは、compact reportと同じ内容を次へexactly one writeする。

```text
/Users/marupro/CODEX/chatGPTweb-to-Terminal/outbox/response.txt
```

write後にread、check、retry、watch、recreateしない。即時移動・削除は正常。

## Current pointers

- current accepted state: `CURRENT_STATE.md`
- exact current task: `NEXT_ACTION.md`
- detailed implementation contract: `chatgpt/specs/active/`
- product route: `PRODUCT_IMPLEMENTATION_ROUTE.md`
- old detailed control: `history/record-optimization-20260721/CONTROL_PRE_OPTIMIZATION.md`
