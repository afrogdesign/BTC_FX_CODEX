# CURRENT_STATE

last_updated: 2026-07-21

## Current posture

- current branch: `Ver04-v3` (reported by bounded local git execution)
- accepted repository-cleanup checkpoint: `bff7669`
- accepted Product checkpoint: `0eeb26b` (`P8 issue lifecycle alignment`)
- accepted state checkpoint: `b9ca3f6` (`record P8 actual evidence blocker`)
- accepted M5 implementation checkpoint: `3c7f01d90c3f5cc126cedd9aed294cf67a602c42`
- primary repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- active spec: none
- safety: report-only / human-decided / no automatic order
- push: none

MCP does not independently expose git branch, HEAD, commit objects, or the complete dirty tree. Branch and commit locators come from bounded local-git reports; acceptance-critical source, tests, CLI routes, specs, state paths, and local artifact availability were reviewed directly through MCP.

## Version policy

- `Ver04-v3`: current accepted repository and Product working line
- `Ver05`: reserved for an evidence-backed, explicitly approved, implemented, validated, and accepted M6 change
- M1–M5 acceptance, M5 evidence refresh, and an M6 source-only shadow do not by themselves qualify for `Ver05`

## Product / P state

- P1–P7 accepted
- P8 evidence pipeline accepted and collecting evidence
- P9 blocked pending adequate evidence and human approval

Current P evidence posture:

- actual-backed evidence remains missing / 0 eligible episodes in the latest reviewed P8 artifacts
- `P8-ISSUE-001` remains an evidence-driven `open hypothesis`
- `P8-ISSUE-002`, `P8-ISSUE-003`, and `P8-ISSUE-004` are resolved UI-contract issues
- P9 readiness remains false

## P actual-evidence readiness — accepted no-repeat boundary

`BTCFX-20260721-P8-ACTUAL-EVIDENCE-READINESS-REVIEW` is complete and accepted as a review-only result.

Directly confirmed availability:

- canonical private input directory `local/manual_trade_imports/` is absent
- `logs/csv/manual_actual_trades.csv` is absent
- `logs/csv/manual_actual_orders.csv` is absent
- `logs/csv/manual_actual_positions.csv` is absent
- `logs/csv/manual_trade_episodes.csv` is absent
- `logs/csv/manual_trade_signal_links.csv` is absent
- `local/manual_trade_imports/` is protected by `.gitignore`

Conclusion:

- eligible actual evidence is 0 because no complete private exchange export batch has entered the accepted importer → episode builder → signal linker route
- this is an input-availability blocker, not an importer, linker, or P8 evaluator defect
- no P source implementation is currently required

A new AI must report this accepted state and must not repeat the importer, episode-builder, signal-linker, CLI, or P8 readiness review.

Reopen the P readiness review only when at least one trigger is true:

1. a complete MEXC Trade History / Order History / Position History `.xlsx` batch appears under `local/manual_trade_imports/YYYYMMDD/`;
2. relevant importer, episode-builder, linker, operating-cycle, or P8 evaluator source/tests change;
3. a new generated artifact contradicts the recorded state;
4. the user explicitly requests re-verification.

Canonical decision: `DEC-20260721-012` in `DECISIONS.md`.

## Macro / M state

- M1 accepted
- M2 accepted
- M3 accepted
- M4 accepted
- M5 accepted
- M6 not started and not authorized

Accepted M5 result:

- champion count: 1
- challenger count: 4
- chronological snapshot dates: 6
- winner: `none`
- recommendation: `continue_shadow_collection`
- P8 actual-backed evidence: missing / 0
- production mutation: none

M5 is already implemented. Do not reopen or rewrite the M5 engine merely because no challenger won.

The current M execution plan is:

```text
wait for a gate-relevant evidence change
→ one bounded M5 evidence refresh
→ zero or one proposal-eligible challenger
→ one human-approved M6 proposal
→ source-only shadow
→ bounded validation
→ explicit human adoption decision
→ separate runtime apply when approved
```

Canonical plan:

- `docs/operations/strategy/M5_M6_EXECUTION_PLAN_20260721.md`

Canonical decision:

- `DEC-20260721-013` in `DECISIONS.md`

M6 may not start until M5 identifies one proposal-eligible challenger and the user explicitly approves one bounded proposal.

## Current selected action

The P route is parked on human private input. While that blocker remains, the selected M-route action is the M5 evidence-refresh trigger defined in `NEXT_ACTION.md`.

Do not run the heavy M5 bundle daily. A refresh is eligible after a gate-relevant change, normally at least seven new eligible JST dates after the accepted 2026-07-21 cutoff, new P8 actual evidence, an accepted M1/M3 comparison-basis change, or explicit user instruction.

## Repository model

Repository cleanup remains accepted. Active implementation areas remain `src/`, `tools/`, `scripts/`, `tests/`, `docs/operations/`, and `chatgpt/specs/active/`.

Generated evidence and raw private inputs remain ignored and uncommitted under `local/` or `logs/` unless a separate artifact contract explicitly says otherwise.

## Safety boundary

- report-only
- not `FORMAL_GO`
- human decides all trades and all adoption
- no automatic order
- no raw exchange export or generated actual CSV commit
- no automatic gate, threshold, scoring, classifier, notification, mail, runtime, or Phase promotion
- no frozen runtime repo access without an explicit `RUNTIME_TASK`
