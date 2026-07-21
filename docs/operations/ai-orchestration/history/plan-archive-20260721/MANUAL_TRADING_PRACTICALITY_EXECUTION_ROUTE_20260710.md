# Manual Trading Practicality Execution Route

## Metadata

- repo: `afrogdesign/BTC_FX_CODEX`
- created_at: `2026-07-10`
- status: active AI execution route
- purpose: future ChatGPT / Codex / AI agents が manual trading practicality plan を段階的に実行するための制御文書
- primary plan: `docs/operations/strategy/MANUAL_TRADING_PRACTICALITY_IMPROVEMENT_PLAN_20260710.md`
- safety: report-only / not `FORMAL_GO` / no automatic order / human decides manually

---

## 1. Purpose

この文書は、manual trading practicality improvement planを、future AIが飛ばさず、混ぜず、独自に緩和せず実行するための導線である。

対象テーマ:

- 本採用候補が少なすぎる問題
- over-suppression
- A/B/C/STOP operator action layer
- scenario identity / lifecycle
- duplicate candidate compression
- actual trade ground truth
- long/short非対称評価
- notification action wording
- offline replay
- human-approved tuning review

このrouteは計画承認を意味するが、production tuning承認ではない。

---

## 2. Required read order

manual trading practicalityに関する作業では、次の順で読む。

```text
1. AGENTS.md
2. docs/operations/ai-orchestration/START_HERE.md
3. docs/operations/ai-orchestration/CURRENT_STATE.md
4. docs/operations/ai-orchestration/NEXT_ACTION.md
5. docs/operations/ai-orchestration/CONTROL.md
6. docs/operations/ai-orchestration/PRODUCT_IMPLEMENTATION_ROUTE.md
7. docs/operations/ai-orchestration/MANUAL_TRADING_PRACTICALITY_EXECUTION_ROUTE_20260710.md
8. docs/operations/strategy/MANUAL_TRADING_PRACTICALITY_IMPROVEMENT_PLAN_20260710.md
9. phase固有のspec / source / tests
```

branchはchat historyやファイル名から推測しない。

```text
git status --short --branch
CURRENT_STATE.md
CONTROL.md
```

を照合する。

---

## 3. AI responsibility split

### ChatGPT / planning AI

- repo状態確認
- evidence解釈
- phase選択
- active spec作成
- success criteria確定
- human approval判断
- Codex prompt作成
- 完了後レビュー

### Codex / implementation worker

- active specに従う実装
- narrow validation
- local commit
- checkpoint taskのみpush
- compact report

### Human

- production threshold変更承認
- gate変更承認
- notification behavior変更承認
- runtime変更承認
- actual manual trade運用判断
- live / automatic behavior承認

---

## 4. State machine

```text
Read current state
→ Confirm current phase
→ Check chatgpt/specs/active
→ If active spec is empty, create one next-phase spec only
→ Review spec against plan and current evidence
→ Obtain human approval when required
→ Implement one phase
→ Validate
→ Review result
→ Archive completed spec
→ Update NEXT_ACTION only when next posture changes
→ Continue to next phase
```

### Active spec rule

- active specが空ならsource実装へ進まない。
- 次phaseのactive spec作成だけを行う。
- active specがある場合は、そのspecを正本とする。
- active specが計画またはcurrent stateと矛盾する場合は、実装せずspec修正taskにする。
- 完了したspecはarchiveへ移す。

---

## 5. Anti-skip and anti-drift rules

- 一度に複数phaseを実装しない。
- importer、linking、coverage、classifier、surface integrationを1taskへまとめない。
- actual trade ground truth前にproduction thresholdを変更しない。
- offline hypothesisをproduction configへ直接転記しない。
- A/B/C/STOPを既存gateの置換として実装しない。
- `trade_execution_gate`を緩和しない。
- `phase1b_lite_gate`を変更しない。
- `opportunity_gate`を緩和しない。
- `trend_flip_confirmed_up`単独を強評価へ戻さない。
- candidate row数を独立scenario数として扱わない。
- no_ohlcv / unresolvedを勝敗へ混ぜない。
- single exampleからtuningしない。
- runtime変更を通常taskへ混ぜない。
- live mail送信をoffline/shadow taskへ混ぜない。
- actual trade raw exportをcommitしない。
- old runtime execution repoを通常taskでread/edit/runしない。

---

## 6. Phase route

| Phase | Objective | Primary input | Output | Human approval |
|---|---|---|---|---|
| P0 | plan / AI route整備 | current repo / evidence | strategy plan / execution route | user approved |
| P1 | importer active spec | plan / current import design | `chatgpt/specs/active/...` | spec review before implementation |
| P2 | actual trade importer | approved P1 spec / local fixtures | normalized local CSV / tests | no production tuning approval |
| P3 | trade-to-signal/scenario linking | imported trades / notification logs | link CSV / confidence | linkage policy review |
| P4 | coverage / scenario normalization | outcomes / OHLCV / candidates | coverage report / scenario model | model review |
| P5 | offline A/B/C/STOP classifier | normalized scenarios / outcomes | report-only classifier / comparison | no production use |
| P6 | historical replay | P5 output / resolved data | baseline-vs-hypothesis report | review required |
| P7 | shadow surface | approved replay findings | HTML/local report shadow display | explicit display approval |
| P8 | human manual trial | shadow output / actual trade capture | manual decision events | human operates manually |
| P9 | evidence-backed tuning review | adequate samples / actual PnL | approved tuning proposal | explicit human approval required |

---

## 7. Phase details

## P0: Plan and routing

Status: complete when this route and the main strategy plan are connected from startup documents.

No source, gate, threshold, notification, runtime change.

## P1: Manual actual trade import active spec

Work ID:

```text
BTCFX-20260710-MTP-ACTUAL-TRADE-IMPORT-SPEC
```

Purpose:

```text
既存のBTCFX-20260702-MEXC-ACTUAL-TRADE-IMPORTER候補を、
manual trading practicality planへ接続するactive specを作成する。
```

P1で確定する項目:

- accepted local xlsx filenames / patterns
- raw export local-only policy
- no API policy
- canonical CSV schemas
- source timezone / JST normalization
- symbol normalization
- side normalization
- open / close / fill semantics
- fee fields
- realized PnL fields
- duplicate import key
- idempotent import behavior
- malformed row handling
- privacy-safe fixtures
- generated output commit policy
- CLI interface
- unit tests
- completion criteria
- P3 linkingとの責務境界

P1では実装しない。

## P2: Importer implementation

Allowed:

- local xlsx read
- deterministic normalization
- local generated CSV
- tests with sanitized fixtures
- report-only summaries

Not allowed:

- exchange API
- account endpoint
- order endpoint
- secrets
- raw export commit
- `paper_positions.csv`への混合

## P3: Actual trade linking

Link targets:

- notification / signal
- later scenario ID

Initial factors:

- open time after mail
- side match
- symbol match
- entry price proximity
- competing signal count
- manual confirmation

Confidence:

- high
- medium
- low
- ambiguous
- manual_confirmed

Performance claimsはhigh + manual_confirmedを優先する。

## P4: Coverage and scenario normalization

Required outputs:

- no_ohlcv root-cause categories
- resolved coverage rate
- scenario identity proposal
- duplicate compression ratio
- lifecycle state model
- signal-to-scenario mapping
- invalidation / expiry semantics

P4完了前にcandidate row数から通知数を決めない。

## P5: Offline classifier

Classifier outputs:

- `A_FORMAL`
- `B_CHECK_15M`
- `C_WATCH_ZONE`
- `STOP_OR_EXIT`

Rules:

- report-only
- no production config mutation
- long/short separate
- regime separate
- warnings visible
- existing gate results retained

## P6: Historical replay

Required comparisons:

- strict current baseline
- A only
- A + B
- A + B + C observation
- long / short
- regime
- scenario type
- notification count
- duplicate count
- TP1-first / SL-first
- MFE / MAE
- missed opportunity
- over-suppression

No decision should be based only on aggregate win rate.

## P7: Shadow surface

Allowed:

- local report
- render-only HTML
- no-send preview
- dashboard shadow panel

Not allowed:

- live notification trigger change
- production threshold change
- runtime restart without explicit task

## P8: Human manual trial

Required event semantics follow:

```text
docs/operations/strategy/VER04_V1_MANUAL_15M_WIN_DEFINITION_20260702.md
```

Record:

- mail signal / scenario ID
- human checked time
- action class
- side
- entry / watch / skip / exit / take-profit
- actual price
- actual R
- reason
- result

## P9: Tuning review

Entry conditions:

- actual trade import functioning
- linking confidence acceptable
- scenario normalization stable
- adequate resolved sample
- long/short split available
- explicit human approval

P9 creates a tuning proposal first. It does not automatically change code or config.

---

## 8. Quality gates

### Data gate

- no_ohlcv rate is reported
- unresolved rows separated
- timestamp normalization verified
- duplicate imports controlled
- scenario duplication measured

### Evaluation gate

- A and B separated
- long and short separated
- regime separated
- PF / R included
- actual vs proxy distinguished

### Operator gate

- next action is clear
- zone is visible
- 15m confirmation is visible
- invalidation is visible
- safety boundary is visible
- Big Chance is not presented as entry permission

### Change gate

- threshold / gate / notification / runtime changes require explicit human approval

---

## 9. Source ownership

| Concern | Source of truth |
|---|---|
| overall practicality plan | `MANUAL_TRADING_PRACTICALITY_IMPROVEMENT_PLAN_20260710.md` |
| AI phase execution | this file |
| current repo posture | `CURRENT_STATE.md` / `CONTROL.md` |
| immediate task | `NEXT_ACTION.md` |
| product route | `PRODUCT_IMPLEMENTATION_ROUTE.md` |
| manual win definition | `VER04_V1_MANUAL_15M_WIN_DEFINITION_20260702.md` |
| active implementation spec | `chatgpt/specs/active/` |
| accepted history | `MILESTONES.md` |

---

## 10. Next exact task

```text
BTCFX-20260710-MTP-ACTUAL-TRADE-IMPORT-SPEC
```

Task type:

```text
DOCS-ONLY / ACTIVE-SPEC-CREATION
```

Expected output:

```text
chatgpt/specs/active/20260710_manual_actual_trade_importer.md
```

The exact filename may be adjusted only if a same-date naming convention already exists.

Scope:

- read current importer design
- define schema and safety contract
- define tests and completion criteria
- do not implement source
- do not import real account files
- do not change runtime

---

## 11. Completion definition for the full route

The route is successful when:

1. actual trades can be imported safely from local exports.
2. actual trades can be linked to notification and scenario evidence.
3. candidate rows are compressed into independent scenarios.
4. A/B/C/STOP can be replayed offline without changing current gates.
5. operator output clearly states what to check on 15m.
6. A and B performance are measured separately.
7. long and short are evaluated separately.
8. over-suppression and turning misses are measurable.
9. actual PnL calibrates proxy evaluation.
10. any production tuning remains human-approved and reversible.


---

## 12. Import-path reconciliation requirement

Phase P1 must read:

```text
docs/operations/ai-orchestration/VER04_V1_IMPLEMENTATION_READINESS_PACKAGE_20260702.md
docs/operations/strategy/VER04_V1_SELF_IMPROVEMENT_LOOP_FINAL_DESIGN_20260702.md
```

The earlier readiness package references:

```text
docs/mexc_csv/
```

The later final design references:

```text
local/manual_trade_imports/YYYYMMDD/
```

P1 must inspect the actual repo and `.gitignore`, then choose one canonical local-only raw input path.

Requirements:

- do not leave two active canonical paths
- do not move or delete existing private files in the spec task
- do not commit raw exports
- document compatibility or migration behavior
- prefer a path that is clearly outside source-controlled documentation when repo evidence supports it
- stop and report a specific blocker if safe canonicalization cannot be decided from repo evidence
