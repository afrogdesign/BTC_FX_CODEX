# Macro P9 Champion/Challenger Proposal Engine

## Metadata

- phase: M5
- work_id: `BTCFX-20260721-MACRO-P9-CHAMPION-CHALLENGER-PROPOSAL-ENGINE`
- status: approved for bounded source implementation
- safety: report-only / not FORMAL_GO / no automatic order / human decides manually

## Objective

Implement a deterministic offline champion/challenger proposal engine for issue diagnosis and proposal ranking. It must not mutate production behavior or become an implicit production input.

## Accepted baselines

- M1 accepted at `663288b`
- M2 accepted at `8aee427`, with docs checkpoint `c2eed44`
- M3 accepted at `d576862`, recommendation `continue_shadow_collection`
- M4 accepted at `ea89e61`
- M4 HTML/JSON/Markdown is review evidence only and must not become a production input

## Explicit inputs

Required: M1 `macro_structure_volatility_events.csv`, `macro_level_reliability.csv`, `macro_missed_move_diagnostics.csv`, and `macro_structure_volatility_replay.json`; M3 `macro_next_regime_events.csv`, `macro_next_regime_policy_episodes.csv`, and `macro_next_regime_replay.json`; an explicit champion manifest; and an explicit bounded proposal-space manifest.

Optional: P8 trial-facts CSV and P8 deterministic trial-report JSON. Absent optional evidence is missing actual evidence, never favorable evidence.

## Proposal-space boundary

The proposal space may use only parameters already exposed by the accepted M1 replay CLI and recorded in M1 method metadata. The exposed names are:

- `signals`, `ohlcv_15m`, `ohlcv_1h`, `ohlcv_4h`
- `output_events_csv`, `output_levels_csv`, `output_misses_csv`, `output_json`, `output_md`
- `cutoff_utc`, `left_window`, `right_window`, `replace_output`
- `performance_start_utc`, `performance_end_utc`

Input/output paths and publication controls are manifest wiring, not optimization levers. A proposal-space entry must identify which accepted parameter it changes and may not invent additional names. M3 family allowlist, candidate/status semantics, 3H primary horizon, gates, and production Big Chance behavior remain frozen.

Use one-parameter-at-a-time challengers plus explicitly declared combinations, with a maximum of 64 challengers. Candidate IDs, ordering, fingerprints, and reruns must be deterministic. No arbitrary Python, expressions, templates, plugin loading, or generated source code are allowed.

## Replay and evaluation

- invoke accepted replay functions directly when an accepted callable exists; do not chain subprocesses
- event-time evidence only, with chronological rolling champion/challenger comparison
- use identical eligible opportunities and date denominators
- primary horizon: `3h`; `6h`, `12h`, and `24h` are diagnostic only and cannot select a winner
- report UP/DOWN, structure, price-location, volatility, reliability, and JST-date concentration splits
- preserve independent candidate/baseline episode identity
- future outcomes cannot alter forecast construction or episode boundaries

## Ranking and recommendation

Allowed recommendation values are `reject`, `continue_shadow_collection`, and `eligible_for_human_reviewed_proposal`.

Rank by deterministic Pareto comparison, not precision alone. Eligibility requires validation pass, both directions represented, coverage/data-quality pass, no single-date dependence, and strict validation non-degradation for guarded precision, recall, opposite-move, false-warning, whipsaw, and burden metrics. Proxy-only challengers may be ranked.

`eligible_for_human_reviewed_proposal` additionally requires P8 practical readiness and eligible actual-backed evidence. Missing actual evidence or false readiness fails closed to at most `continue_shadow_collection`. Eligibility is proposal permission only and never production permission.

## Outputs and CLI

Publish exactly `macro_p9_challenger_results.csv`, `macro_p9_issue_diagnosis.csv`, `macro_p9_proposal_engine.json`, and `macro_p9_proposal_engine.md` using atomic four-output replacement with rollback and compact JSON stdout without raw rows or private paths.

Add CLI route `run-macro-p9-proposal-engine` with explicit input/output paths, champion manifest, proposal-space manifest, and replace flag.

## Issue categories

- reliable level missed
- level reliability unstable
- rejection/break/acceptance/reclaim event missed
- pressure or imbalance unavailable
- travel corridor missed
- wrong next-regime side
- correct macro thesis but poor tactical timing
- over-defensive suppression
- excessive false warning
- one-sided or date-concentrated evidence
- actual evidence missing or conflicting

## Required focused tests

Cover proposal manifest schema/version fail-closed, unknown/non-allowlisted parameters, maximum challenger count, deterministic IDs, champion inclusion exactly once, event-time/future-field isolation, same-opportunity/date-denominator comparison, 3H primary horizon, diagnostic-horizon non-selection, Pareto ranking, one-sided/date-concentrated/data-quality failure, missing P8/actual evidence, readiness with actual-backed evidence, no production mutation, atomic rollback, byte determinism, and actual CLI parser/dispatch.

## Completion and archive condition

M5 completion requires focused tests, one bounded local replay, and four complete deterministic outputs, with no production/runtime/notification/mail behavior changes. ChatGPT acceptance is required before archive or M6. M6 remains human-reviewed and is not authorized by M5 completion.

M4 has been accepted as local render-only evidence. M5 source implementation is the next task and has not started.

## Implementation note — bounded FIX-01

Historical 15-minute source bytes were not retained, so the bounded evaluation uses one fresh self-contained local bundle produced through the accepted public OHLCV fetch path. Only `left_window` and `right_window` are optimization levers; the evaluation windows remain fixed. The exact CLI route is `run-macro-p9-proposal-engine`. The implementation remains pending ChatGPT acceptance.

## Implementation note — bounded FIX-02

M1 validation comparison now uses only `recommendation_gate.validation_policy_metrics.reliable_level_acceptance_corridor`; no fallback policy or full-period metric is permitted. M1 and M3 guarded metrics remain explicitly namespaced. Candidate results expose separate structural, comparison, Pareto, and proposal eligibility states. Chronological rolling snapshots are event-time bounded, while 6H/12H/24H diagnostics are stored but non-selecting. The bounded result remains report-only with `continue_shadow_collection`; M5 acceptance remains pending ChatGPT review.

## Implementation correction — bounded FIX-03 continuation

FIX-03 now uses true cutoff-bounded snapshot replay, with the champion replay cached once per date and reused across challengers. Lightweight module/CLI validation is complete; heavy actual-bundle acceptance, the second full replay, and byte-identity verification are deferred to a separate task. M5 acceptance remains pending ChatGPT review.

## Implementation correction — bounded FIX-04

FIX-04 closes the rolling review blockers: split degradation now follows the direction of every guarded metric and missing split metrics fail closed; challenger summaries use only eligible candidate-specific rolling snapshots with no terminal/champion fallback; rolling snapshots retain sanitized candidate issue lineage; and champion snapshots require quality, required metrics, date concentration, and same-date alignment before comparison. Focused module/CLI tests and a lightweight deterministic full-orchestration fixture passed. Full actual-bundle acceptance, a second full replay, and actual four-output byte-identity acceptance were not run. M5 acceptance remains pending ChatGPT review; M6 remains unauthorized.

## Implementation correction — bounded FIX-05

FIX-05 integrates candidate-specific rolling M1/M3 split evidence into actual challenger gating across every snapshot date. Split degradation and missing required metrics now fail closed, while candidate issue lineage remains private to diagnosis and public rolling evidence exposes only counts and deterministic fingerprints. The meaningful lightweight orchestration fixture passed through the real rolling, split, gating, issue publication, and four-output paths. The actual full bundle, second full replay, and actual-bundle four-output byte identity were not run. M5 acceptance remains pending ChatGPT review; M6 remains unauthorized.

## Implementation correction — bounded FIX-06

FIX-06 makes final challenger Pareto and issue diagnosis use same-date rolling champion evidence; terminal champion summaries are no longer challenger comparison fallbacks. Wholly missing split dimensions fail closed, champion direction counts use the existing threshold, and candidate diagnosis reads the actual M1 `root_cause` and `reason_codes` fields. Public lineage remains count/fingerprint only. Lightweight focused validation passed; the actual full bundle, second full replay, and actual-bundle byte identity were not run. M5 acceptance remains pending ChatGPT review; M6 remains unauthorized.

## Implementation correction — bounded FIX-07

FIX-07 makes failed or malformed champion cache entries fail closed without exception leakage, records champion direction insufficiency explicitly, prevents runless challengers from inheriting terminal champion validation evidence, preserves rolling failure reasons, and requires the accepted M1 `opportunity_id`, `root_cause`, and `reason_codes` lineage fields. P8 insufficiency is reported only when the P8 gate itself fails. Lightweight focused validation passed; the actual full bundle, second full replay, and actual-bundle byte identity were not run. M5 acceptance remains pending ChatGPT review; M6 remains unauthorized.

## Implementation correction — bounded FIX-08

FIX-08 aligns M3 quality with the accepted `data_quality.coverage_continuity_pass` contract; rolling quality, direction, and concentration failures retain explicit reasons; champion manifest IDs are bound to deterministic parameters; and fresh champion identity includes M1/M3 replay JSON. No-rolling final publication remains empty and fail-closed. P8-insufficient, P8-sufficient/no-Pareto, and P8-sufficient/winner paths passed lightweight orchestration tests, with diagnostic horizons remaining non-selecting. The actual full bundle, second full replay, and actual-bundle byte identity were not run. M5 acceptance remains pending ChatGPT review; M6 remains unauthorized.


## Acceptance — 2026-07-21

M5 was accepted after direct ChatGPT review of FIX-08 source, focused tests, CLI behavior, and one bounded actual-bundle run at implementation checkpoint `3c7f01d`.

Accepted evidence:

- one full bounded execution; 31 planned candidate-run units
- 6 chronological snapshot dates
- champion count 1 and challenger count 4
- all 4 challengers structurally valid but comparison-ineligible
- no Pareto-dominant or proposal-eligible challenger
- winner `none`
- recommendation `continue_shadow_collection`
- primary gate horizon `3h`; 6h/12h/24h diagnostic-only
- P8 actual evidence missing and one report-global insufficiency row
- exactly four fresh outputs
- no temporary path or raw opportunity-ID publication
- no source, runtime, production, notification, mail, gate, threshold, or order mutation during acceptance

This acceptance approves the deterministic fail-closed offline proposal engine. It does not approve a challenger, production tuning, M6, or any runtime/adoption change.
