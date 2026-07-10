# P7 Manual Operator Shadow Surface — Completed Specification

## Metadata

- phase: P7
- status: completed and accepted
- implementation mode: report-only / offline / existing public HTML detail page
- preceding accepted phase: P6 historical replay (`e870bd8`)
- safety: not FORMAL_GO / no automatic order / human decides manually

## Objective

Add a visible shadow panel to the existing public notification detail HTML. It displays how the current report snapshot would be classified as `A_FORMAL`, `B_CHECK_15M`, `C_WATCH_ZONE`, or `STOP_OR_EXIT`. This is human decision support only.

The panel renders through `build_notification_detail_html()`. It must not change notification subject/body/trigger/send count/publish routing. There is no live mail send in this phase.

## Surface and data boundary

The chosen surface is the existing public HTML detail page. Use only the current result payload supplied to the renderer and small read-only wrappers around the existing current-result candidate/signal mapping in `src/storage/csv_logger.py`.

Do not read or write replay output, actual trades, manual decisions, outcomes, `paper_positions.csv`, raw exports, APIs, account data, or secrets. Rendering must not mutate the result payload or write CSV files.

## Classifier reuse

P7 uses the same P5 implementation from `src/feedback/manual_operator_classifier.py`. Expose one public pure single-candidate helper and make the existing batch path use the same underlying helper. Do not duplicate A/B/C/STOP conditions or thresholds. Threshold defaults remain unchanged comparison values; production gates, scoring, no-trade logic, and threshold behavior are untouched.

## Shadow adapter

Planned implementation file: `src/feedback/manual_operator_shadow_surface.py`.

The adapter produces `schema_version: manual_operator_shadow_surface.v1` with `surface_status` equal to `ready`, `no_current_candidate`, `insufficient_evidence`, or `malformed`. Rows are deterministic and sorted by class priority (`STOP_OR_EXIT`, `A_FORMAL`, `B_CHECK_15M`, `C_WATCH_ZONE`), side, candidate type, and shadow row ID.

Use wording `current candidate snapshot` or `shadow candidate`; do not call it an independent P4 scenario. Do not use future outcomes, replay results, actual PnL, or human-decision evidence.

Sanitized row fields may include only shadow row ID, classification status, operator class, side, candidate status/type, required human check, reason/warning codes, gate evidence, entry/zone, invalidation, TP1, and TP2. Never expose paths, account/order identifiers, manual notes, private values, raw rows, or generated output paths.

## Operator wording and safety

- `A_FORMAL`: 現行の厳格条件を通過したshadow候補。15分足確認後も人間が判断する。
- `B_CHECK_15M`: 15分足確認候補。エントリー許可ではない。
- `C_WATCH_ZONE`: 監視専用。条件改善またはupgrade待ち。
- `STOP_OR_EXIT`: 新規停止・利確・撤退・保護を人間が確認する。自動決済ではない。

Every panel visibly states: `SHADOW / REPORT ONLY`, `not FORMAL_GO`, `no automatic order`, and `human decides manually`.

## HTML placement and degradation

Insert one compact panel after the existing answer-first operator action/reason area and before lower diagnostic/advanced sections. Preserve the current conclusion, chart, Long/Short cards, Value Defense, Big Chance, and diagnostics.

No current candidate renders a neutral unavailable panel. Insufficient evidence remains insufficient and is never promoted to C. Malformed optional shadow input fails closed inside the panel and must not fail the complete detail page.

## Planned files and prohibitions

Planned files: `src/feedback/manual_operator_shadow_surface.py`, `src/feedback/manual_operator_classifier.py`, `src/storage/csv_logger.py`, `src/notification/detail_page.py`, and focused tests. `main.py` is not required.

Do not edit production gates, notification trigger/sender, summary generation, trade modules, runtime/launchd, APIs, secrets, or order behavior.

## Required tests

The public single-candidate helper must match batch P5 results for A, B, C, STOP, and insufficient evidence. Test read-only current-result wrappers, deterministic A/B/C/STOP rows, no-candidate and malformed fail-closed behavior, safe HTML labels and price layers, absence of raw identifiers/paths/private values, byte-identical repeated rendering, existing detail-page tests, and no-send smoke.

## Implementation and runtime boundary

Next implementation validation is limited to targeted classifier, shadow-surface, detail-page, and no-send tests plus render-only smoke and task-file diff checks. No live mail send occurs. Checkpoint push and runtime apply are separate tasks; runtime verification must confirm the active process and remain reversible. Do not alter launchd configuration. P8 must not start automatically.

## Acceptance

P7 is accepted only when the sanitized deterministic shadow panel is visible in the existing public HTML, P5/P7 share one classifier, all targeted tests and render-only validation pass, and the report-only safety boundary remains intact.

## Completion record

- implementation_commit: `dec4cb0`
- acceptance_correction_commit: `74047f1`
- accepted_checkpoint: `74047f14bceb4644ec3ab86eb5d0e5c23d97541c`
- targeted_tests: 74 passed
- shadow_test_methods: 10
- render_smoke: pass
- runtime_repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- launchd_label: `com.afrog.btc-monitor`
- runtime_apply: pass
- verified_replacement_pid_at_apply: `18923` (process observed at apply verification time, not a permanent runtime identity)
- real_mail_sent: false
- live_output_boundary_violated: false

P7 changed only the existing public detail HTML shadow surface. Production gate, scoring, and threshold behavior were not changed; notification subject, body, trigger, and send count were not changed; and no automatic order was introduced. P8 was not started by this closeout.
