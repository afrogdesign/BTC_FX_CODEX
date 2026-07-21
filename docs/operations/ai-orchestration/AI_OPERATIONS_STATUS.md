# AI Operations Status

last_updated: 2026-07-21
status: canonical conclusion of the A route

## Purpose

A計画は、btc_monitor本体の機能計画ではない。

長いCodex prompt、重複validation、thread handoff、report確認コストを減らすために行ったChatGPT/Codex運用実験である。

## Why it started

M1〜M5周辺の開発で次が顕在化した。

1. natural-language promptへstate、scope、safety、validation、dirty-tree、report形式を詰め込みすぎた
2. implementation debuggingとheavy replay acceptanceが同じloopに入った
3. Codex reportとChatGPT reviewが重複した
4. thread切替時に同じcontextを繰り返した
5. 小さなtaskでもorchestration記録が増えた

問題認識自体は正しかった。

## Phase result

| Phase | Objective | Result |
|---|---|---|
| A1 | task/report schema、validator、prompt renderer | accepted |
| A2 | one low-risk pilot | accepted |
| A3 | manifest/JSON routeを通常標準にする | superseded |
| A4 | optional CWT integration | not planned |

A2によって、strict routingは技術的に機能する一方、通常の小さなtaskでは作業量を増やすことが確認された。

## Final decision

通常経路:

```text
ChatGPT compact prompt
→ one bounded Codex implementation
→ matching tests / small fixture
→ compact text report
→ ChatGPT MCP review
```

optional strict tooling:

- task manifest
- `validate-task`
- `render-prompt`
- JSON task report
- `validate-report`

これらは次の場合だけ検討する。

- heavy acceptanceでexact commandとwork unitsを固定する
- acceptance taskでsource edit禁止を機械的に固定する
- runtime task
- checkpoint push
-複数stage・複数worktreeでownership alignmentがacceptance-critical
- reviewed commit bindingが必要

通常の一ファイル修正、docs-only task、通常Python実装、matching unittestでは使用しない。

## Useful outcomes retained

A計画から残すもの:

- implementationとheavy acceptanceの分離
- heavy runのChatGPT明示承認
- one full bounded acceptance runを原則上限とする
- Codex reportをproofではなくlocatorとして扱う
- same-thread delta prompt
- scope外変更とunrelated dirty差分の分離
- report形式だけでretaskしない
- A1 toolingを例外用として保存する

## What is discontinued

- manifest/JSON routeの標準化
- report self-validationを通常taskへ要求すること
- reportを検証するための追加Codex task
- CWT integrationを独立目的として進めること
- orchestration frameworkをproduct backlogより優先すること

## Current rule

A計画は完了した運用実験として扱う。

新しいA phaseは作らない。A1 toolingを再利用する場合は、直接reviewよりmaterialな証拠を追加する理由をtaskごとに明示する。

## References

- canonical workflow: `AI_WORKFLOW.md`
- stable controls: `CONTROL.md`
- overall plan: `MASTER_PLAN.md`
- accepted A specs: `chatgpt/specs/archive/20260721_ai_task_manifest_*`
- historical design documents: `history/plan-archive-20260721/`
