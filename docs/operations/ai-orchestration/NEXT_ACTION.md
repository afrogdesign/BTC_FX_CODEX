# NEXT_ACTION

last_updated: `2026-07-25`
authoritative_closure: `wp8_f4eeadd6864d736e7c457490d362ac0b`
reviewed_head: `d43a67db7e8b339316e6a2ffd14144bf362b5aa8`

## Latest P operational evidence acceptance

- implementation commit: `1224a31f1126bdc17564192193e00a8224ee927e`
- artifact locators: `local/reports/p_evidence/p_current_generation/latest/` and `local/reports/p8_daily_v2/wp5_wp6_acceptance_20260724_fix2/`
- source HEAD was resolved automatically as `1224a31f1126bdc17564192193e00a8224ee927e`; cutoff was `2026-07-24T02:15:00Z` from the selected cycle manifest.
- snapshot policy is `latest_accepted_snapshot_as_of_cutoff`; selected classification/trial rows are `907/346`, with v1/v4 cohorts `679/228` and `297/49`.
- P9 v2 is `baseline_available`, but frozen proposal thresholds and frozen validation cohort remain missing. No formal gate change is approved.
- evidence is report-only/descriptive with no automatic causality; production, notification, runtime, mail, and order behavior remain unchanged.

## Current task — P current-generation evidence collection

Status: `waiting_for_material_input`

The only authorized next P task is bounded, delta-only collection of current-generation evidence for `manual_operator_classifier.v4`.

Start this task only after at least one material new accepted input exists for either:

- the cumulative v4 classification cohort; or
- the cumulative v4 proxy-trial cohort.

When the trigger exists:

1. process only the new evidence and minimum matching lineage;
2. preserve actual and proxy evidence as separate facts;
3. update cumulative evidence and the P8/P9 report-only manifests deterministically;
4. reassess readiness without inventing thresholds or mixing generations;
5. stop before proposal selection, validation-policy approval, source behavior change, or production adoption.

Until the trigger exists, perform no P implementation, replay, runtime operation, notification change, threshold freeze, proposal approval, or production action.

Safety boundary:

- P9 remains `collecting`;
- no proposal is selected or under review;
- H2 through H8 remain unauthorized;
- no gate, Phase1, classifier, score, threshold, notification, canonical-link, runtime, launchd, mail, schedule, production, `FORMAL_GO`, or automatic-order change;
- human decides manually.
