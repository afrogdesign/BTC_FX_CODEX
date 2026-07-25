---
title: "P WP7 Evidence Review and Proposal Selection"
date: 2026-07-25
status: implementation-authorized
work_id: P-GENERATION-ALIGNMENT-WP7
program: P
package: WP7
branch: Ver04-v5
reviewed_base: 1688d9508378d0b2d734dd73cfe41e6f0622c976
safety_boundary: "report-only proposal review / no source behavior change / no approval / no runtime or notification change / no automatic order"
---

# P WP7 — Evidence Review and Proposal Selection

## 1. Decision

WP0 through WP6 are accepted.

WP7 reviews the accepted evidence and records whether any production-behavior proposal is sufficiently supported for human review.

WP7 does not edit source behavior. It does not approve a proposal. It does not freeze thresholds on behalf of the human. It does not start validation. It does not authorize WP8 behavior changes.

The current accepted evidence is insufficient to select a behavior-changing proposal because:

- current daily classifier is `manual_operator_classifier.v4`
- cumulative classification cohort is `manual_operator_classifier.v1`
- cumulative proxy-trial cohort is `manual_operator_classifier.v1`
- the current v4 classification cohort is missing
- the current v4 proxy-trial cohort is missing
- claim-specific proposal thresholds are not frozen
- a frozen validation cohort is absent
- readiness state is `collecting`

The accepted evidence does establish a notification-usefulness baseline:

- accepted high/medium actual attribution: 58
- descriptive low/ambiguous/no-candidate actual rows: 91
- automatic causal claims: 0
- canonical link replacement: false

This baseline permits candidate assessment, but not behavior selection or approval.

## 2. Inputs

Read only these accepted artifacts:

```text
local/reports/p8_daily_v2/wp5_wp6_acceptance_20260725/p8_daily_manifest_v2.json
local/reports/p8_daily_v2/wp5_wp6_acceptance_20260725/p9_readiness_v2.json
local/reports/p8_daily_v2/wp5_wp6_acceptance_20260725/p8_daily_summary_v2.md
local/reports/p8_daily_v2/wp5_wp6_acceptance_20260725/p9_readiness_migration_report.md
local/reports/p_evidence/wp3_wp4_acceptance_20260725/latest/evidence_manifest.json
local/reports/p_evidence/wp3_wp4_acceptance_20260725/latest/modern_attribution_report.json
local/reports/p_evidence/wp3_wp4_acceptance_20260725/latest/modern_attribution_ledger.csv
```

Do not read raw exchange exports.
Do not modify any accepted input artifact.

## 3. Outputs

Generate exactly:

```text
local/reports/p_proposals/wp7_review_20260725/proposal_review.json
local/reports/p_proposals/wp7_review_20260725/proposal_review.md
```

These generated artifacts remain unstaged and uncommitted.

Commit only:

```text
chatgpt/specs/active/20260725_p_wp7_evidence_review_and_proposal_selection.md
```

## 4. Top-level result

The JSON result must contain:

```text
schema_version
method_version
review_id
review_date
reviewed_generation
input_fingerprints
readiness_state
notification_usefulness_baseline
candidate_reviews
selected_proposal
selection_status
next_evidence_requirements
human_decision_required
production_behavior_change_authorized
safety_boundary
```

Required constants:

```text
schema_version = p_wp7_proposal_review.v1
method_version = p_wp7_evidence_review.v1
review_date = 2026-07-25
selection_status = no_behavior_proposal_selected
selected_proposal = null
human_decision_required = false
production_behavior_change_authorized = false
```

`human_decision_required=false` means there is no eligible proposal currently presented for approval. It does not waive future human approval.

## 5. Candidate set

Review exactly these candidate IDs:

```text
P9-PROP-FORMAL-GATE-ADVISORY
P9-PROP-PHASE1-WATCH-LANE
P9-PROP-NOTIFICATION-BURDEN
P9-PROP-ACTUAL-LINKER-CONFIDENCE
P9-PROP-TURNING-PRECURSOR
P9-PROP-OPERATOR-UI
```

For each candidate record:

```text
proposal_id
claim
required_cohort
current_behavior
proposed_behavior
expected_benefit
safety_risk
available_evidence
offline_result
missing_evidence
frozen_validation_plan
rollback
eligibility
human_decision
```

Required values:

```text
eligibility = not_eligible
human_decision = not_requested
```

No candidate may be marked eligible, under review, approved, accepted, or production-ready.

## 6. Candidate assessment rules

### 6.1 Formal gate advisory handling

Record that advisory tokens are visible and shared semantics exist, but current evidence does not authorize changing formal gate interpretation.

Missing evidence must include:

- current v4 cumulative classification cohort
- current v4 cumulative proxy-trial cohort
- advisory-only blocker cohort
- claim-specific frozen thresholds
- time-split frozen validation cohort
- false-positive and false-negative review
- explicit H4 human decision

Safety risk is high because gate relaxation can affect formal execution eligibility.

### 6.2 Phase1 watch lane

Record that a distinct chart-check/watch lane is a plausible product proposal, but current evidence does not quantify its incremental value or notification burden under a stable v4 cohort.

Missing evidence must include:

- stable current-generation watch cohort
- side-specific outcomes
- actual versus proxy separation
- notification burden baseline
- frozen validation plan
- explicit H4/H5 human decision

### 6.3 Notification burden

Record that backlog 110 is not new notification burden and must not be used as a burden metric.

Missing evidence must include:

- sent-notification episode count
- suppression/cooldown count
- notification-kind distribution
- repeated-notification burden
- human chart-check/usefulness confirmation
- frozen burden threshold
- explicit H5 human decision

### 6.4 Actual linker confidence

Record the accepted evidence:

- baseline episodes: 149
- baseline links: 149
- accepted high/medium actual: 58
- descriptive low/ambiguous/no-candidate: 91
- automatic causal claims: 0
- canonical link replacement: false

This may justify future data-quality or review-queue work, but not automatic canonical-link replacement or gate/classifier changes.

Missing evidence must include:

- reviewed ambiguous/low labels
- precision estimate by confidence tier
- stable modern-metadata coverage
- frozen linker validation cohort
- explicit human approval for any canonical migration

### 6.5 Turning precursor

Record that the current accepted P-route artifacts do not provide a claim-specific turning-precursor cohort suitable for proposal selection.

Do not import unrelated Macro proposal-engine results as P-route approval evidence.

### 6.6 Operator UI

Record that operational and evidence data exist, but usability evidence is absent.

Missing evidence must include:

- defined operator task
- usability observations
- error or confusion cases
- proposed UI-only change
- rollback or feature flag
- explicit human product decision

UI work must not be justified by actual PnL alone.

## 7. Selection rule

Set:

```text
selection_status = no_behavior_proposal_selected
selected_proposal = null
```

because the current readiness state is `collecting`, the current classifier cohorts are missing, thresholds are not frozen, and no frozen validation cohort exists.

Do not select the least risky candidate merely because it is available.
Do not invent thresholds.
Do not reinterpret notification usefulness as formal execution readiness.
Do not treat 58 accepted actual links as causal proof.

## 8. Next evidence requirements

Record a deterministic ordered list:

1. collect cumulative `manual_operator_classifier.v4` classification cohort
2. collect cumulative `manual_operator_classifier.v4` proxy-trial cohort
3. define one issue-specific claim scope
4. measure the claim-specific cohort and exclusions
5. freeze minimum requirements before validation
6. freeze calibration and validation time windows
7. validate without mixing unresolved or no-OHLCV rows into performance facts
8. present one bounded proposal for human decision

No production action follows automatically.

## 9. Markdown report

The Markdown report must summarize:

- accepted WP3/WP4 and WP5/WP6 evidence
- current readiness state
- notification usefulness baseline
- current v4 versus cumulative v1 cohort gap
- all six candidate assessments
- why no behavior proposal was selected
- next evidence requirements
- explicit statement that WP8 has no approved behavior proposal to implement
- report-only safety boundary

## 10. Determinism and privacy

- standard library only
- deterministic sorted JSON
- stable Markdown
- no current clock
- no absolute paths
- no raw rows in JSON or Markdown
- no account, order, fill, or private export identifiers
- input SHA-256 fingerprints recorded
- deterministic review_id from sorted input fingerprints and reviewed generation

## 11. Validation

Create no source module and no test module.

Use one bounded Python standard-library command or a small temporary command to generate the two artifacts from the accepted inputs.

Validate:

- six candidate IDs exactly once
- every candidate `not_eligible`
- every human decision `not_requested`
- selected proposal is null
- selection status is `no_behavior_proposal_selected`
- readiness state is `collecting`
- accepted usefulness actual is 58
- causal claims are 0
- canonical replacement is false
- current v4 cohorts are missing
- production behavior authorized is false
- no absolute paths or private rows
- deterministic rerun bytes using a temporary second output only

Do not run a full replay or full test suite.

## 12. Safety boundary

```text
report-only evidence review
no source behavior edit
no gate change
no classifier change
no threshold change
no notification behavior change
no canonical link replacement
no readiness adoption
no proposal approval
no runtime, launchd, mail, or notification operation
no production adoption
no order behavior
human decides manually
```

## 13. Acceptance boundary

WP7 acceptance means only that the evidence review and candidate proposal assessments are reproducible and correctly conclude that no behavior proposal is currently eligible.

WP7 acceptance does not authorize:

- H2 cumulative baseline adoption
- H3 threshold approval
- H4 formal gate or Phase1 change
- H5 notification trigger change
- H6 classifier or threshold change
- H7 runtime/mail apply
- WP8 source behavior change
- production adoption
- automatic order
