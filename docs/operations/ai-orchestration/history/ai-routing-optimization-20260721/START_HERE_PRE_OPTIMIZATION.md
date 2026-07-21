# START_HERE

このファイルは `btc_monitor` の最短入口です。長い履歴は読まず、現在の作業に必要な正本だけを辿ります。

## 30秒で現在地を確認する

1. `AGENTS.md`
2. `docs/operations/ai-orchestration/START_HERE.md`
3. `docs/operations/ai-orchestration/CURRENT_STATE.md`
4. `docs/operations/ai-orchestration/NEXT_ACTION.md`
5. `chatgpt/specs/active/` にある対象spec

運用規則の確認が必要な場合だけ `CONTROL.md` を読みます。

`MILESTONES.md`、`TASK_LEDGER.md`、`handoffs/CURRENT_HANDOFF.md` は通常のstartup readではありません。

## Repo doctrine

| 用途 | Path | Rule |
|---|---|---|
| primary working repo | `/Users/marupro/CODEX/100_MCP_Server/btc_monitor` | 通常のinspection、edit、test、git |
| frozen old runtime repo | `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor` | 明示されたruntime task以外ではread/edit/runしない |

- ChatGPTは `AFROG_Business_MCP` をprimary inspection pathとして使う。
- branchはchat historyから推測せず、`git status --short --branch`で確認する。
- 通常taskはlocal edit、targeted validation、local commit、compact report。
- pushは明示されたcheckpoint taskだけで行う。

## 記録ファイルの役割

| File | 内容 |
|---|---|
| `CURRENT_STATE.md` | 現在受理済みの状態と未受理blocker |
| `NEXT_ACTION.md` | 現在の作業を1件だけ記録 |
| `CONTROL.md` | 変化しにくい運用・安全・git規則 |
| `MILESTONES.md` | 受理済みの大きな節目のみ |
| `DECISIONS.md` | product・設計上の重要判断 |
| `TASK_LEDGER.md` | 過去Work IDの検索用台帳 |
| `chatgpt/specs/active/` | 実装中の唯一の詳細仕様 |
| `chatgpt/specs/archive/` | 受理済み仕様 |

詳細は `README.md` を参照します。

## Active spec rule

- source実装前に `chatgpt/specs/active/` を確認する。
- active specがある場合は、そのspecを実装正本とする。
- active specがrouteまたは安全境界と矛盾する場合は、実装せずspec correctionにする。
- completed specはChatGPT acceptance後にarchiveへ移す。
- active specが空なら、未承認のsource実装へ進まない。

## Task別の追加読取

- product route: `PRODUCT_IMPLEMENTATION_ROUTE.md`
- manual practicality route: `MANUAL_TRADING_PRACTICALITY_EXECUTION_ROUTE_20260710.md`
- macro route: `docs/operations/strategy/MACRO_STRUCTURE_VOLATILITY_SELF_IMPROVEMENT_PLAN_20260720.md`
- checkpoint: `CHECKPOINT_RUNBOOK.md`
- runtime handoff: `RUNTIME_PULL_HANDOFF.md`
- accepted history: `MILESTONES.md`
- Work ID検索: `TASK_LEDGER.md`を全文ではなく限定検索

## Safety boundary

- report-only
- not `FORMAL_GO`
- human-decided
- no automatic order
- no API keys、secrets、private/account/order endpoints
- no raw exchange export commit
- no unapproved runtime restart、launchd、mail、notification behavior change
- no unapproved `paper_positions.csv` integration
- `trade_execution_gate`、`phase1b_lite_gate`、`opportunity_gate`を根拠なく緩和しない
- candidate row数を独立機会数として扱わない
- unresolved / no-OHLCVを勝敗へ混ぜない

## MCP transmission privacy

MCP request bodyにはaddress形式の文字列や機微識別子をそのまま入れない。

- address形式は `[redacted-email]`
- 機微識別子は `[redacted-id]`
- raw source行を転載せず、filename、symbol、section、抽象要約でinspectionする
- responseで得た機微値を次のrequestへ引き継がない

## Source-of-truth priority

```text
repo実体
→ active spec
→ CURRENT_STATE / NEXT_ACTION / CONTROL
→ product route
→ MILESTONES / TASK_LEDGER / handoff history
→ chat history
```

旧版の詳細文書は `docs/operations/ai-orchestration/history/record-optimization-20260721/` に保存されています。
