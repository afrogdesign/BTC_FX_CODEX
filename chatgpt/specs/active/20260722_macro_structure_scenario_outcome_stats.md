---
title: M-STATS1・macro scenario outcome counts shadow evaluator
date: 2026-07-22
tags:
  - btc_monitor
  - macro-structure
  - report-only
---

# M-STATS1 shadow evaluator

M-STATS1 is an opt-in, local-only evaluator for immutable M-HYP1 operator artifacts. It counts observed scenario outcomes at 6H, 12H, and 24H horizons. It does not fetch market data and is not part of the macro runtime, operator renderer, latest page, notification, mail, publication, LaunchAgent, or schedule.

## Method

```text
schema_version = macro_structure_scenario_outcome_stats.v1
method_version = macro_structure_scenario_outcome_stats.v1
```

The input is an explicit operator artifact root containing `operator_*/macro_structure_operator.json`. The first valid observation of each `scenario_id` establishes its cohort start. Each horizon selects the earliest valid later artifact at or after the target and no more than one 4H cadence interval late. Missing eligible artifacts are `immature`.

Retained structural events after cohort start and no later than the selected artifact determine the result. Confirmation before invalidation is `continuation`; invalidation before or at the same timestamp is `rejection`; no decisive event is `indeterminate`.

## Evidence boundary

Counts are reported only. Fewer than 20 mature rows in the reported group is `insufficient`; 20 or more is `descriptive_only`. No ratio, probability, confidence, or execution instruction is produced.

The evaluator remains report-only / human decides manually / no automatic order.
