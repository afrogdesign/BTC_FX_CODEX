# P8 / P9 Issue Register

last_updated: 2026-07-11
status: active
source_of_truth: `docs/operations/strategy/P8_P9_EVIDENCE_TUNING_OPERATING_SPEC_20260711.md`

## Rules

- 会話だけで問題を管理しない。
- 単一例は`open hypothesis`として記録し、production tuningの根拠にしない。
- deterministic evidence、actual-backed evidence、人間のUI観察を分離する。
- unresolved / no_ohlcvを勝敗へ混ぜない。
- issueの解決は実装完了ではなく、再評価で改善が確認された時点とする。

## Status values

- `open hypothesis`
- `confirmed usability issue`
- `confirmed data/logic issue`
- `collecting evidence`
- `eligible for P9 proposal`
- `approved for implementation`
- `shadow validation`
- `resolved`
- `rejected`

## Issues

### P8-ISSUE-001 — Global STOP masks side-specific opportunity

- category: classifier logic / over-suppression
- status: open hypothesis
- first_seen: 2026-07-11
- evidence:
  - source inspection: global `no_trade_flags` returns `STOP_OR_EXIT` before side-specific B/C evaluation
  - one observed Short-zone case where market later moved down
- risk: valid opposite-side manual-review opportunity may be hidden
- required evidence:
  - occurrence count
  - opposite-side zone outcome
  - side/regime/setup split
  - actual-backed count
  - current-B/C-without-global-STOP counterfactual
- first baseline (2026-07-11): 364 STOP rows, 449 opposite-side candidates, 0 counterfactual B, 0 counterfactual C, 0 qualified rows; no actual evidence supplied
- baseline status remains `open hypothesis`; a single baseline does not establish tuning eligibility
- next action: P8 evidence pipeline measures; P9 may propose side-aware STOP only after adequate evidence
- production change: prohibited until P9 approval

### P8-ISSUE-002 — Main decision and Big Chance hierarchy is unclear

- category: UI / operator comprehension
- status: confirmed usability issue
- first_seen: 2026-07-11
- evidence: user interpreted auxiliary Long hypothesis as the primary prediction despite main WAIT and STOP
- risk: operator may act on a lower-priority hypothesis
- next action: P9 UI proposal should separate primary action, auxiliary hypothesis, and invalidation state

### P8-ISSUE-003 — Raw classifier payload is exposed

- category: UI / explainability
- status: confirmed usability issue
- first_seen: 2026-07-11
- evidence: slash-separated internal fields are displayed in operator cards
- risk: next action, side, and reason are difficult to understand
- next action: human summary first; technical details under a collapsed diagnostic section

### P8-ISSUE-004 — STOP card side identity is unclear

- category: UI / actionability
- status: confirmed usability issue
- first_seen: 2026-07-11
- evidence: two STOP cards do not make Long/Short identity sufficiently prominent
- risk: operator cannot quickly determine which thesis is stopped
- next action: explicit `LONG` / `SHORT` card header and side-specific action sentence

### P8-ISSUE-005 — Manual trial was incorrectly described as full manual logging

- category: documentation / operations
- status: resolved
- first_seen: 2026-07-11
- correction:
  - market outcomes are deterministic and automatic
  - actual trades are imported and linked from local exports
  - human input is limited to ambiguous intent and exceptional cases
- resolution source: `P8_P9_EVIDENCE_TUNING_OPERATING_SPEC_20260711.md`

## P9 proposal eligibility

An issue may become `eligible for P9 proposal` only when:

- evidence cutoff and versions are reproducible
- unresolved/no_ohlcv are separated
- candidate rows are scenario-deduplicated
- Long/Short and relevant regime/setup splits are available
- the issue has more than a single anecdotal example unless it is a deterministic bug or safety defect
- actual-backed evidence is included where the claim concerns actual trading performance
- a validation window can be reserved

## Change-class separation

Never combine these in one tuning task without explicit approval:

1. data/identity defect
2. UI/wording/hierarchy
3. shadow classifier logic
4. comparison threshold
5. production gate
6. notification behavior
7. runtime behavior
