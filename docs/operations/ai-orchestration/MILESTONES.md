# MILESTONES

このファイルは受理済みの大きな節目だけを記録する。FIX単位の経過、未受理結果、current taskは記録しない。

## 2026-07-21 — M5 champion/challenger proposal engine accepted

- accepted source checkpoint: `3c7f01d90c3f5cc126cedd9aed294cf67a602c42`
- acceptance Work ID: `BTCFX-20260721-MACRO-P9-CHAMPION-CHALLENGER-PROPOSAL-ENGINE-ACCEPTANCE-01`
- one bounded actual local-bundle run completed
- 1 champion、4 challengers、6 chronological snapshot dates
- true cutoff-bounded M1/M3 replay and same-date champion baseline
- primary gate horizon: `3h`; longer horizons are diagnostic only
- winner: `none`
- recommendation: `continue_shadow_collection`
- P8 actual evidence: missing
- no comparison-eligible、Pareto-dominant、or proposal-eligible challenger
- report-only posture preserved; M6 remains unauthorized

M5 acceptance is implementation/evidence acceptance. It is not challenger adoption or production tuning approval.

## 2026-07-21 — A1 AI task-manifest contract foundation accepted

- accepted checkpoint: `13527dc69bfc3b2b17fc96ab2ab6f5a8d8ef495f`
- strict task/report validation、canonical SHA、compact rendering、fail-closed report alignment、reviewed-commit binding、and write-once outbox accepted
- focused static evidence was sufficient; no heavy run was required
- A1 does not activate canonical routing、transport integration、automatic execution/acceptance、M6、runtime、notification、mail、or production behavior

## 2026-07-21 — A2 low-risk manifest pilot accepted

- accepted implementation checkpoint: `95840ef4de0aa7d88972f35df37b7dac9f078f65`
- implementation manifest SHA: `250a51807a470a17619d6ee85f3019af782577a41c40a436f5e14e3ef7022660`
- first bounded docs-only pilot using the A1 manifest, rendered launcher, machine report, and report validator
- exact three-file implementation scope
- revision-3 read-only review report validated successfully
- no heavy validation and no product or runtime posture change
- pilot evidence showed that strict routing should remain optional rather than become the normal path

## 2026-07-21 — M4 hierarchy render shadow accepted

- accepted checkpoint: `ea89e61`
- local deterministic render-only hierarchy comparison
- grouped operator wording and source trace accepted
- tactical status safety、NONE/disagreement、future-field exclusion accepted
- deterministic three-directory publication and rollback accepted
- live UI、notification、mail、runtime、policy promotionは未承認

## 2026-07-21 — M3 next-regime offline shadow accepted

- accepted checkpoint: `d576862`
- event-time offline candidate/baseline comparison
- exact family allowlist and fail-closed conflict handling
- primary gate horizon: `3h`
- recommendation: `continue_shadow_collection`
- production Big Chanceは変更なし

## 2026-07-21 — M2 macro auxiliary shadow accepted

- accepted source checkpoint: `8aee427`
- optional、disabled-by-default auxiliary shadow
- bounded result: 124 events、94 levels、33 independent opportunities
- recommendation: `continue_shadow_collection`
- runtime、notification、mail、production analysisは変更なし

## 2026-07-21 — M1 macro evidence layer accepted

- accepted checkpoint: `663288b`
- reliable 1H/4H structural levels and lifecycle
- prior-only reliability history
- separate volatility、expansion、direction、target evidence
- independent opportunity denominator and chronological validation
- deterministic atomic replay outputs
- offline/report-only acceptance

## 2026-07-11 — P8 evidence pipeline accepted

- deterministic trial facts and market-path evaluation
- actual-backed evidence remains optional and fail-closed
- exception-only human review queue
- P9 readiness is proposal eligibility only
- no automatic tuning or production mutation

## 2026-07-10 — Manual trading practicality P1–P7 route completed

```text
P1 importer contract
→ P2 importer hardening
→ P3 trade linkage and ground truth
→ P4 scenario identity and decision events
→ P5 offline A/B/C/STOP classifier
→ P6 historical replay
→ P7 shadow surface
```

The route preserves strict formal gates and adds operator-action layers without treating them as execution permission.

## Ver04-v2 product direction

- primary objective: notification mail → human 15m check → practical manual trading support
- automatic trading remains later-stage only
- safety posture: report-only / not `FORMAL_GO` / no automatic order / human decides manually

## Current transition

- `MASTER_PLAN.md` is the canonical overall planning entrypoint
- Product/P is the main axis; P8 evidence collection continues and P9 remains evidence-gated
- Macro/M is a supporting axis; M1〜M5 are accepted and M6 remains unauthorized
- AI/A is a completed operations experiment; A1 tooling is optional, A3 is superseded, and A4 is not planned
- the next task is one smallest useful Product task selected from current P8/M5 evidence

## Detailed history

- pre-optimization milestone document: `history/record-optimization-20260721/MILESTONES_PRE_OPTIMIZATION.md`
- task-level history: `TASK_LEDGER.md`
- implementation evidence: git history and compact reports
