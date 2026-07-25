# NEXT_ACTION

## Authoritative current work — 2026-07-25

- last updated: `2026-07-25`
- authoritative decision source: ChatGPT review of `f4966efe2891e87e2a095293721b48bdad0ec091` and ChatGPT acceptance of `581361fff179f7030193d28e3980900ca47d28f4`
- WP0: accepted
- WP1: accepted
- authorized next work: `WP2 — Semantic Identity and Versioning`
- WP2 posture: report-only / spec-first / no production behavior change
- WP2 does not change gates, classifier, thresholds, scoring, notifications, mail, runtime, or Product P9 state, and does not authorize automatic order
- WP2 must define identity, generation, schema/method version, legacy separation, and comparison boundaries; it does not authorize source changes unless a later separately reviewed task does so

This section is authoritative. The sections below are preserved as historical accepted evidence and prior operational guidance; where they conflict with this section, this section wins. The existing B-evidence collection restrictions remain applicable to B-evidence tuning, but they do not block the separate WP2 contract/spec task. Frozen-runtime references below are historical and non-binding because frozen runtime is obsolete and out of scope.

## Current accepted state

- P5 hard STOP and advisory semantics are accepted at commit `85a93cb`.
- Bounded C watch eligibility is accepted at commit `6d1d9ff`.
- Separate P8 exact-link C observation is accepted at commit `74c24f8`.
- B candidate-status producer/classifier alignment is accepted at commit `68664ca`.
- Historical public OHLCV implementation is accepted at commit `4734c61`.
- Macro obstruction-ID resolution is accepted at commit `f08a815`.
- The operator-surface and P8 recovery route is completed and archived at:
  - `chatgpt/specs/archive/20260723_operator_surface_and_p8_recovery_blueprint.md`

### Macro runtime acceptance

One authorized Macro target execution completed successfully on `2026-07-23`.

- finished at: `2026-07-23T20:45:53.001833+09:00`
- snapshot run: `run_1a31a398e48e9aa0c27c`
- snapshot: `macro_snapshot_1a31a398e48e9aa0c27c`
- history: `history_445e535393ee7dbe4702`
- operator: `operator_79239ad03128a4007022`
- snapshot/history/operator steps: success
- source state: current / continuous / ok
- operator HTML: present and non-empty
- report-only: true
- private actual-trade input: false
- automatic order allowed: false

### P8 recovery acceptance

One P8 recovery execution completed for report date `20260723`.

- actual episodes: 149
- actual links: 149
- actual input status: `provided`
- output root: `logs/p8_operating_cycles/20260723`
- actual eligible rows: 2
- actual high-confidence rows: 0
- actual medium-confidence rows: 2
- unique actual episodes used: 2
- resolved proxy events: 40
- unresolved proxy events: 4
- P9 initial readiness: false
- P9 practical readiness: false
- proxy and actual evidence remain separate
- no phase promotion occurred

### Existing B evidence

- The focused formal-B proxy evidence rebuild remains accepted under `local/p8_b_evidence_rebuild_20260723/`.
- Formal B evidence contains 12 covered, resolved, proxy-only observations:
  - resolved positive: 7
  - resolved negative: 5
  - TP1 first: 5
  - TP2 first: 2
  - SL first: 5
  - useful/aligned: 7
  - failed/too aggressive: 5
- Setup-family split:
  - `market_entry`: 4 positive / 1 negative
  - `limit_retest`: 3 positive / 4 negative
- All 12 formal B observations are short-side.
- There is no formal long-side B evidence and no exact actual B episode link.
- Exact C observations remain 8 rows / 8 unique episodes.
- Classifier remains `manual_operator_classifier.v4`.

## Decision

Retain `B_CHECK_15M` as a bounded human-review category. Current evidence does not authorize:

- promotion to A;
- classifier, threshold, gate, score, setup-rule, candidate-status, or policy changes;
- automatic execution;
- profitability, probability, expected-return, or notification-causality claims;
- P9 or `FORMAL_GO` approval.

The five `market_entry` observations remain too few for a rule change. `limit_retest` remains mixed. Proxy and actual evidence must remain separate.

## Authorized next work

There is no immediate implementation or runtime recovery package authorized.

Resume bounded delta-only evidence collection only after at least one material new input exists:

1. newly accepted formal B facts;
2. formal long-side B observations;
3. an exact actual B episode link.

When a material delta exists:

- process only the new evidence and the minimum matching lineage;
- preserve existing accepted bundles;
- keep actual and proxy evidence separate;
- reassess readiness truthfully;
- do not start P9 unless a later human-approved specification explicitly authorizes it.

## Bounded observation

The accepted Macro runtime completed its core snapshot/history/operator route, while the non-blocking scenario-stats sidecar reported `stats_duplicate_event_conflict`. Do not repeat the Macro run or open a broad diagnosis automatically. Create a separate bounded diagnosis only if the failure repeats or materially affects operator delivery or evidence collection.

## Waste and safety controls

- do not rerun the `20260723` P8 cycle;
- do not rerun the fixed B evidence bundle;
- do not repeat the accepted Macro kickstart;
- do not generate health artifacts when status plus referenced artifacts already prove acceptance;
- do not poll or retry unchanged runtime commands;
- do not clean unrelated dirty changes;
- do not access the frozen runtime repo without an explicit `RUNTIME_TASK`;
- do not change classifier, threshold, gate, score, setup rules, candidate status, policy, notification, mail, schedule, order behavior, or P9 readiness;
- preserve report-only / not `FORMAL_GO` / no automatic order / human decides manually.
