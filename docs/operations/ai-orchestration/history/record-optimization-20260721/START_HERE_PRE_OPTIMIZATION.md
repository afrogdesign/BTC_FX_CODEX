# START_HERE

新しい ChatGPT / Codex / future AI agent は、まずこのファイルから読み始めます。

## Repo doctrine

| Label | Path | Rule |
|---|---|---|
| MCP/Codex primary working repo | `/Users/marupro/CODEX/100_MCP_Server/btc_monitor` | 通常の read / edit / test / git はここで行う |
| Frozen old runtime execution repo | `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor` | 通常 orchestration / product task では edit/run/inspect しない |

- runtime execution repo は current editing target ではない。
- runtime execution repo への反映は、MCP working repoでclean checkpointを作ったあとに明示taskで行う。
- ChatGPTはAFROG MCPをprimary repo inspection pathとして使う。
- GitHubはcheckpoint / history / sync用であり、毎回のreviewのdefault read pathではない。
- Codexは明示指示がない限りMCP working repoだけを編集する。
- normal Codex taskはlocal edit + local validation + local commit + compact reportが基本。
- pushは`CHECKPOINT_PUSH` taskだけで行う。

## Current product objective

現時点の最優先目的は自動売買ではない。

```text
notification mail を受け取った人間が、
15分足を確認し、
攻めの姿勢で勝てる manual trading support system を作る。
```

manual trading practicalityの現在の重点は次である。

```text
厳格なA候補の品質を維持する。
B候補で人間が15分足確認できる機会を増やす。
C候補で未到達の機会を監視する。
STOPで新規停止・利確・撤退を支援する。
候補行をscenarioへ圧縮する。
actual trade ground truthで評価を補正する。
```

これはproduction tuningの自動承認ではない。

## Branch source rule

branchはchat historyや古い文書の固定値から推測しない。

次を照合する。

```text
git status --short --branch
docs/operations/ai-orchestration/CURRENT_STATE.md
docs/operations/ai-orchestration/CONTROL.md
```

矛盾がtask判断へ影響する場合は停止する。

## Tiered read order

### Tier 0 / always

1. `AGENTS.md`
2. `docs/operations/ai-orchestration/START_HERE.md`

### Tier 1 / state needed

1. `docs/operations/ai-orchestration/CURRENT_STATE.md`
2. `docs/operations/ai-orchestration/NEXT_ACTION.md`
3. `docs/operations/ai-orchestration/CONTROL.md`

### Tier 2 / by task type only

#### Product direction / manual trading practicality

1. `docs/operations/ai-orchestration/PRODUCT_IMPLEMENTATION_ROUTE.md`
2. `docs/operations/ai-orchestration/MANUAL_TRADING_PRACTICALITY_EXECUTION_ROUTE_20260710.md`
3. `docs/operations/strategy/MANUAL_TRADING_PRACTICALITY_IMPROVEMENT_PLAN_20260710.md`
4. `docs/operations/strategy/VER04_V1_SELF_IMPROVEMENT_LOOP_FINAL_DESIGN_20260702.md`
5. `docs/operations/strategy/VER04_V1_MANUAL_15M_WIN_DEFINITION_20260702.md`
6. `docs/operations/strategy/VER04_V1_INTEGRATED_PRODUCT_PLAN.md`

この順序は、次のtaskで必須。

- 本採用候補が少ない問題
- over-suppression
- A/B/C/STOP
- manual entry候補
- scenario lifecycle
- duplicate candidate / duplicate notification
- actual trade ground truth
- long/short機会調整
- notification action wording
- offline replay
- evidence-backed tuning review

#### Phase4 observation / cue review

- `docs/operations/ai-orchestration/PHASE4_SELF_IMPROVEMENT_CONTROL_PLAN_20260707.md`

#### Codex prompt work

- `docs/operations/ai-orchestration/PROMPTS.md`
- `docs/operations/ai-orchestration/MINI_CODEX_RULES.md`
- `docs/operations/ai-orchestration/PROMPT_PREFLIGHT_CHECKLIST.md`

#### Checkpoint

- `docs/operations/ai-orchestration/CHECKPOINT_RUNBOOK.md`

#### Runtime pull handoff

- `docs/operations/ai-orchestration/RUNTIME_PULL_HANDOFF.md`

#### Accepted history

- `docs/operations/ai-orchestration/MILESTONES.md`

#### Handoff only

- `docs/operations/ai-orchestration/handoffs/CURRENT_HANDOFF.md`

#### Historical lookup only

- `docs/operations/ai-orchestration/TASK_LEDGER.md` by search / latest rows only

`TASK_LEDGER.md` と `handoffs/CURRENT_HANDOFF.md` はdefault startup readではない。

## Active spec rule

- implementation前に`chatgpt/specs/active/`を確認する。
- active specが空ならsource実装へ進まない。
- 次phaseのactive spec作成だけを行う。
- active specがある場合は、そのspecを実装正本とする。
- active specがcurrent routeと矛盾する場合は、実装せずspec修正taskにする。
- completed specはarchiveへ移す。

## Current manual-trading phase rule

manual trading practicality routeは次の順で進める。

```text
P1 actual trade importer spec
→ P2 importer implementation
→ P3 trade-to-signal/scenario linking
→ P4 coverage and scenario normalization
→ P5 offline A/B/C/STOP classifier
→ P6 historical replay
→ P7 shadow surface
→ P8 human manual trial
→ P9 evidence-backed tuning review
```

複数phaseを1taskへまとめない。

## Default avoid list

- `.venv312/`
- `logs/` unless explicitly scoped
- generated CSV / report / HTML
- raw exchange exports under `local/manual_trade_imports/`
- full `docs/operations/ai-orchestration/TASK_LEDGER.md`
- historical task notes unless explicitly named
- frozen old runtime execution repo

## Quick rules

- repo-local docsをchat historyより優先する。
- current branchを自動推測しない。
- 通常taskでruntime repoを読まない、走らせない、編集しない。
- raw exchange exportsをcommitしない。
- actual human tradesを`paper_positions.csv`へ混ぜない。
- `ACTIVE_*`を`FORMAL_GO`として扱わない。
- A/B/C/STOPを既存gateの置換として扱わない。
- `trade_execution_gate`を緩和しない。
- `phase1b_lite_gate`を勝手に変更しない。
- `opportunity_gate`を勝手に緩和しない。
- `trend_flip_confirmed_up`を根拠なく強評価へ戻さない。
- no_ohlcv / unresolvedを勝敗へ混ぜない。
- candidate row数を独立機会数として扱わない。
- production behavior変更前にexplicit scopeとhuman approvalを確認する。
- ChatGPTがscopeを決め、Codexには固定済みの小さいtaskを渡す。


---

## 2026-07-10 repo-audit correction

The manual trading practicality route must use the current repository implementation as evidence.

The repository already contains an early MEXC actual-trade importer, trade-to-signal linker, and manual ground-truth report in `tools/log_feedback.py`, with matching targeted tests. Therefore:

```text
P1 = importer hardening contract/spec
P2 = existing importer hardening
P3 = existing linker / ground-truth pipeline audit and hardening
P4 = scenario identity, coverage, and human decision-event schema
```

Do not describe P2 or P3 as greenfield work.

Exchange exports establish actual order/fill/position/fee/PnL facts. They do not establish why a human entered, watched, skipped, exited, or took profit. Avoided-loss and missed-opportunity evaluation requires a separate human decision-event record and market counterfactual evidence.

At the 2026-07-10 repo-audit starting point, the then-current active spec was:

```text
chatgpt/specs/active/20260710_manual_actual_trade_importer.md
```

At that audit starting point, the then-current next action was:

```text
BTCFX-20260710-MTP-ACTUAL-TRADE-IMPORT-HARDENING
```

The current phase and current task of record are maintained in `CURRENT_STATE.md` and `NEXT_ACTION.md`; the historical audit text above is not a fixed current value.


---

## MCP transmission privacy rule

This rule applies to ChatGPT when sending any request body to AFROG MCP or another MCP tool.

- Do not include any email-address-formatted string in the MCP request body.
- Replace all test or example email-like values with `[redacted-email]` before transmission.
- Do not quote a source-code or test-file line when that line contains an email-address-formatted string.
- When inspection is required, use a safe search term, filename, function name, summary, or line-number description that does not reproduce the email-like value.
- If an MCP response contains such a value, do not repeat it in a later MCP request body.
- This is a ChatGPT-side transmission rule and is separate from Codex implementation scope unless a user explicitly creates a Codex task for it.

This rule is mandatory across new threads because `START_HERE.md` is a Tier 0 startup document.


### MCP consent-prompt avoidance clarification

ChatGPT should continue using MCP read and write operations proactively when they are the safest and most direct way to complete the task.

The objective is not to disable MCP writes. The objective is to prevent avoidable consent prompts by sanitizing every MCP request body before transmission.

Mandatory handling:

- Build each write request from a clean summary instead of copying raw source or test lines.
- Remove address-formatted contact strings and replace them with `[redacted-email]`.
- Remove sensitive identifier-like values and replace them with `[redacted-id]`.
- Do not quote a source or test line that contains either class of value.
- Use safe filenames, function names, section names, line-number descriptions, and abstract summaries for inspection and edits.
- Do not carry a sensitive value returned by one MCP call into a later MCP request.
- Continue MCP writes after sanitization; do not stop or defer ChatGPT-completable work merely because a write is involved.
- If a consent prompt still appears, cancel that specific request, rebuild a smaller clean request, and retry once without reproducing the flagged value.
