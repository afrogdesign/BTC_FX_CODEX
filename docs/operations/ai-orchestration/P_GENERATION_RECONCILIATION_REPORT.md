# P Generation Reconciliation Report

更新日: 2026-07-25  
Work ID: `P-GENERATION-ALIGNMENT-WP0-WP1`

## 1. Executive summary

WP0は現行sourceのcontract owner・version・consumer・authorityを整理し、ChatGPT reviewでacceptedされた。WP1はactual evidenceが既に存在する現行truthをcanonical docsへ反映したが、canonical-document consistency FIXが必要であり、現時点では未受理である。source、test、gate、threshold、classifier、notification、runtimeは変更していない。

## Final ChatGPT review disposition — 2026-07-25

- WP0: accepted。
- WP1: accepted after FIX1 and NEXT_ACTION precedence reconciliation。
- FIX1 commit `581361fff179f7030193d28e3980900ca47d28f4`: accepted。
- `docs/operations/ai-orchestration/NEXT_ACTION.md`: existing content was preserved and the collision was resolved by adding an authoritative precedence section。
- WP2 — Semantic Identity and Versioning: authorized as the sole next report-only/spec-first package。
- Product P9 and all production behavior changes remain unauthorized。

## 2. Verified repository baseline

| item | verified value |
|---|---|
| repository | `/Users/marupro/CODEX/100_MCP_Server/btc_monitor` |
| branch | `Ver04-v5` |
| starting HEAD | `34c751fb9f257d188dc1ed2680df90fbe29855d1` |
| reviewed base | `34c751fb9f257d188dc1ed2680df90fbe29855d1` |
| plan SHA-256 | `63352b8ec78cca8a7215f882a9d5ebeef161f7bd90a2ae2f62e68cfdaa72a76b` at start; unchanged at validation |
| existing staged changes | none at start |
| known collision | `START_HERE.md`, `NEXT_ACTION.md`, and other user-dirty files were not edited/staged |

計画書内の古いbase/HEAD記載は計画書の内容として保持し、実repo baselineとは混同しない。

## 3. Canonical truth table

| fact | canonical current truth | interpretation |
|---|---|---|
| actual input | `provided` | canonical actual input exists |
| actual episodes / links | `149` / `149` | generated and available |
| actual eligible rows | `2` | current selected eligible evidence |
| confidence | high `0`, medium `2` | quantity/coverage/validation window remain insufficient |
| unique actual episodes used | `2` | do not inflate with all imported rows |
| proxy events | resolved `40`, unresolved `4` | proxy and actual remain separate |
| classifier | `manual_operator_classifier.v4` | version cohort boundary applies |
| Product P9 initial readiness | `false` | not approved |
| Product P9 practical readiness | `false` | both insufficient evidence and current implementation fixed-false must be distinguished |
| Product P9 namespace | `program=P`, `phase=P9` | human approval before proposal/production change |
| Macro proposal namespace | `program=M`, M5/M6 improvement proposal engine | `macro_p9_proposal_engine.v1`; never call this Product P9 |
| P8 daily health | one operating cycle's inputs, lineage, outputs, success/failure | not cumulative readiness |
| P9 cumulative evidence | multi-day/multi-episode, version-consistent proposal eligibility | daily success does not make this true |

現在のblockerはactual evidenceの不存在ではなく、量、side/setup coverage、confidence、validation windowの不足である。actual inputの存在はP9開始、`FORMAL_GO`、production tuningを承認しない。

## 4. Contradictions corrected

- `complete private MEXC export batch missing`、`no actual episode/link pair`、`actual-backed evidence = 0`をcurrent truthから除外し、歴史的snapshot/旧decisionとして扱った。
- P8 daily healthとProduct P9 cumulative readinessを分離した。
- Product P9とMacroの既存`macro_p9_proposal_engine.v1`をprogram namespaceで分離した。
- classifier/method versionを跨ぐ単純比較を禁止し、version不明は`legacy_unversioned`として分離する方針を明記した。
- `AFROG_MCP`を今回の新規/編集部分の名称に統一した。既存dirty・archive/history・active draftの残存は次節で分類する。

## 5. Deferred collisions

| path / item | reason and treatment |
|---|---|
| `docs/operations/ai-orchestration/NEXT_ACTION.md` | HEADから大幅な既存変更があり安全分離不可。衝突セクションはCurrent accepted state、P8 recovery acceptance、Decision、Authorized next work。編集/stageしなかった。`<WP0/WP1受理後>`に置換すべき唯一の次作業は `WP2 — Semantic Identity and Versioning`。 |
| `docs/operations/ai-orchestration/START_HERE.md` | 既存unstaged変更。P/P9とM-OPS5の古いhandoffが衝突するが、今回の安全境界では編集不可。 |
| `AGENTS.md`, `CONTROL.md`, `INITIAL_PROMPT.md` | 既存dirty変更。名称/path・安全境界を今回分として分離できないため未編集。 |
| `AFROG_Business_MCP` occurrences | current dirty filesは衝突、archive/historyは履歴、active draftは未整理候補として分類。今回編集した2文書と更新したcurrent sectionsでは`AFROG_MCP`のみ使用。問題例として計画書に引用された文字列は変更していない。 |
| completed-looking specs under `chatgpt/specs/active/` | acceptanceと後継が一意に証明できないため移動・削除・書換えなし。report-only分類に留めた。 |

`NEXT_ACTION.md`への反映は、既存変更のownerが解消した後の別作業とする。WP2はreport-only/spec-firstで、source、gate、classifier、threshold、notification、runtimeを変更しない。

## 6. Lifecycle reconciliation

正本のlifecycleは次で統一する。

- `active`: 現在認可され未完了の作業契約
- `accepted`: 実装/evidenceをChatGPTが受理済み
- `completed`: 作業系列が終了した事実
- `superseded`: 新しい正本に置換され現在の指示ではない
- archive/history: 履歴であり現行正本を上書きしない

active specの完了候補は、受理と後継を一意に証明できないため、広範なarchive整理を行わない。

## 7. Known source defects not fixed in WP0/WP1

`src/feedback/manual_operator_trial_evidence.py`では`p9_readiness.practical.ready`が`False`固定で生成される。これは「証拠によりfalse」とは別の、既知の設計欠陥/未実装contractである。今回はsourceを変更しない。後続WPでcriteria、version、window、sample条件を明示して実計算へ移行する必要がある。

## 8. Recommended single next action

`WP2 — Semantic Identity and Versioning`

report-only/spec-firstで、field identity、generation、method/schema version、legacy分離、cross-version比較境界を定義する。source、gate、classifier、threshold、notification、runtimeは変更しない。`NEXT_ACTION.md`への反映は既存dirty変更のownerが解消した後に別途行う。

## 9. Safety boundary

report-only / human-decided / no automatic tuning / no automatic phase promotion / no automatic order。P9開始、FORMAL_GO、production tuning、actual CSV再生成/上書き、private/account/order endpoint、mail、runtime/launchd操作、frozen runtime調査は行っていない。

## 10. Validation evidence

- required source paths were inspected read-only; see `P_SYSTEM_CONTRACT_MAP.md`.
- plan SHA-256 was checked at start and end and remained unchanged.
- branch/HEAD and empty staged baseline were checked.
- only Markdown contract/reconciliation docs and clean canonical documentation sections were staged.
- no Python, test, runtime, or generated-data path was added to this task.
