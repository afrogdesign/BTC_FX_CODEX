# CURRENT_STATE

last_updated: 2026-07-21

## Current posture

- recorded working branch: `Ver04-v2`
- primary repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- accepted macro phase: M5 bounded offline champion/challenger proposal engine
- accepted source checkpoint: `3c7f01d90c3f5cc126cedd9aed294cf67a602c42`
- AI-orchestration docs checkpoint: reported commit `5d13c3913dafb10c07add6a9abd25f5955fc900c`
- active product spec: none
- next route: bounded A1 task-manifest foundation spec
- M6: not started and not authorized

Branch and git objects are confirmed by local git at task start. AFROG MCP directly verifies file content and routing state but does not expose `.git` internals.

## Product objective

```text
notification mailを受け取った人間が15分足を確認し、
攻めの姿勢で勝てるmanual trading support systemを作る。
```

現段階は自動売買ではない。

## Safety boundary

- report-only
- not `FORMAL_GO`
- human-decided
- no automatic order
- no API keys、secrets、private/account/order endpoints
- no unapproved runtime、launchd、mail、notification behavior change
- no production scoring、threshold、gate、classifier mutation
- no raw exchange export commit
- no unapproved `paper_positions.csv` integration

## Accepted macro checkpoints

| Phase | Accepted checkpoint | Status |
|---|---|---|
| M1 macro evidence | `663288b` | offline evidence accepted |
| M2 auxiliary shadow | `8aee427` | disabled-by-default shadow accepted |
| M3 next-regime replay | `d576862` | accepted; recommendation `continue_shadow_collection` |
| M4 hierarchy render shadow | `ea89e61` | local render-only evidence accepted |
| M5 proposal engine | `3c7f01d` | offline proposal engine accepted; no eligible challenger |

## M5 acceptance

Acceptance-only execution completed one full bounded run across 6 chronological snapshot dates.

- champion count: 1
- challenger count: 4
- comparison-eligible challengers: 0
- Pareto-dominant challengers: 0
- proposal-eligible challengers: 0
- winner: `none`
- recommendation: `continue_shadow_collection`
- P8 actual evidence: missing
- primary gate horizon: `3h`
- `6h`, `12h`, and `24h`: diagnostic only

Fresh output checkpoint:

- results CSV: `12a7aaf14e95113ddc57b274d0fed06aa95405b020a5783a920336091ae1e633`
- issues CSV: `3a43499ea4673f3653fb00ac6485c2647031ed3a4209efef44fc0e0c4e85af6c`
- JSON: `12947969e02f4476c02d760054d284932f8288628aa07914a158a799ca53425f`
- Markdown: `fdbe8579f466ec17ed4a3a32979c9da9cd8801490eb7f21277f6ececc18803f5`

M5 acceptance is implementation/evidence acceptance. It does not approve a challenger, production tuning, M6, or phase promotion.

## AI-orchestration checkpoint

The post-M5 docs state has been directly verified through MCP:

- active specs contain only `.gitkeep`
- accepted M5 spec is archived
- canonical routing docs are aligned
- stale M5 FIX boundaries were removed from current design docs
- the task-manifest design and replay-simplification plan are separate
- source, tests, local artifacts, and runtime files remain outside the docs checkpoint

The checkpoint commit hash above is the Codex report value because MCP cannot inspect `.git` objects.

## Current route

Create one bounded A1 active spec using:

```text
docs/operations/ai-orchestration/AI_TASK_MANIFEST_AND_ACCEPTANCE_GATE_SPEC_20260721.md
```

A1 is limited to:

- task manifest schema
- task report schema
- examples
- validator and prompt renderer
- focused tests
- task README

Do not start CWT integration, replay-stage/cache redesign, M6, runtime, notification, or production changes.

## Production state

M1-M5 remain offline/shadow evidence. They do not change:

- production Big Chance
- structural-priority UI
- notifications or mail
- runtime schedule
- scoring, thresholds, gates, or classifiers
- APIs, accounts, positions, or orders

## Navigation

- exact current work: `NEXT_ACTION.md`
- stable rules: `CONTROL.md`
- accepted M5 spec: `chatgpt/specs/archive/20260721_macro_p9_champion_challenger_proposal_engine.md`
- A1 parent contract: `AI_TASK_MANIFEST_AND_ACCEPTANCE_GATE_SPEC_20260721.md`
- accepted large checkpoints: `MILESTONES.md`
