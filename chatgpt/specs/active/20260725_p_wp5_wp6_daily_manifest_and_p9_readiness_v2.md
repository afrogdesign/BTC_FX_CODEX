---
title: "P WP5/WP6 Daily Manifest v2 and P9 Readiness v2 Shadow"
date: 2026-07-25
status: implementation-authorized
work_id: P-GENERATION-ALIGNMENT-WP5-WP6
program: P
packages: [WP5, WP6]
branch: Ver04-v5
reviewed_base: 7024746f23251e32ff69cc63d72864a9af6ea446
safety_boundary: "report-only shadow / no schedule or notification change / no readiness adoption / no automatic order / human decides manually"
---

# P WP5/WP6 — Daily Manifest v2 and P9 Readiness v2 Shadow

## 1. Decision

WP0、WP1、WP2、WP3、WP4はacceptedである。

WP5とWP6は、既存P8 daily cycleを変更・再実行せず、既存の日付別P8 outputとaccepted cumulative evidence bundleを読む独立shadow builderとして実装する。

このpackageは次を行う。

- P8 daily manifest v2 shadow
- daily queue delta
- daily actual-attribution delta
- cumulative evidence pointer
- generation/cohort comparison
- ISSUE applicability
- legacy readiness v1とP9 readiness v2の併記
- claim-specific、version-aware、human-gated readiness state
- deterministic migration report

このpackageは次を行わない。

- `manual_operator_operating_cycle.py`の変更
- `manual_operator_trial_evidence.py`の変更
- `tools/run_p8_daily_cycle.py`の変更
- `tools/log_feedback.py`の変更
- launchd、schedule、mail、notification、runtimeの変更
- P8 cycleの再実行
- cumulative baselineのhuman adoption
- P9 proposal approval
- WP8 source behavior change
- production adoption
- threshold、classifier、gate、scoring変更
- automatic order

## 2. Verified accepted inputs

### 2.1 Daily P8 output

Accepted existing daily artifact root:

```text
logs/p8_operating_cycles/20260724/
```

Verified facts:

```text
report_date = 20260724
daily trial facts = 43
daily resolved = 38
daily unresolved = 5
daily no_ohlcv = 0
daily review queue = 110
daily eligible actual = 2
daily actual high = 0
daily actual medium = 2
daily classifier = manual_operator_classifier.v4
daily class distribution = C_WATCH_ZONE:43
daily sides = long:26, short:17
core P4/P5/P8 stages = ok
OHLCV freshness = valid
no automatic tuning = true
```

`issue_001`は`stop_rows=0`、`global_stop_present=false`である。このdaily cycleではISSUE-001を「解決済み」とはせず、`not_applicable_no_stop_population`とする。

### 2.2 Cumulative P evidence

Accepted existing cumulative artifact root:

```text
local/reports/p_evidence/wp3_wp4_acceptance_20260725/latest/
```

Verified facts:

```text
run_id = p_ev_2d243f32b8493fbbaad15a36be0a6a34
cutoff_utc = 2026-07-25T01:05:00.785295Z
evidence facts = 5921
actual episodes = 149
actual links = 149
accepted high/medium actual = 58
low/ambiguous/no-candidate descriptive = 91
automatic causal claims = 0
canonical link replacement = false
```

Version cohort facts:

```text
classification cohort = manual_operator_classifier.v1
proxy trial fact cohort = manual_operator_classifier.v1
current daily classifier = manual_operator_classifier.v4
```

したがってcurrent v4 classifier claimに対する累積v4 classification/trial cohortは未収集である。manifest top-levelのdeclared `classifier_version`だけを根拠にv4 evidenceが存在すると扱ってはならない。`cohort_counts`を実証として使う。

## 3. Source layout

新規source:

```text
src/feedback/p8_daily_manifest_v2.py
src/feedback/p9_readiness_v2.py
tools/build_p8_daily_manifest_v2.py
```

新規tests:

```text
tests/test_p8_daily_manifest_v2.py
tests/test_p9_readiness_v2.py
tests/test_build_p8_daily_manifest_v2_cli.py
```

既存contractを利用する。

```text
src/contracts/generation_identity.py
src/contracts/operator_semantics.py
```

既存sourceは変更しない。

## 4. Public versions

```python
P8_DAILY_MANIFEST_SCHEMA_VERSION = "p8_daily_manifest.v2"
P8_DAILY_MANIFEST_METHOD_VERSION = "p8_daily_manifest_builder.v2"
P9_READINESS_SCHEMA_VERSION = "p9_readiness.v2"
P9_READINESS_METHOD_VERSION = "p9_readiness_evaluator.v2"
```

## 5. General rules

### 5.1 Standard library only

新規moduleとCLIはPython標準libraryだけで動作する。既存contract moduleのimportは可とする。

禁止:

- pandas dependency
- dependency installation
- network
- exchange API
- current clockをidentityへ使用
- git/HEADの暗黙取得
- absolute pathのreport露出

### 5.2 Explicit generation

callerは次を明示する。

```text
program=P
runtime_generation
source_head
cutoff_utc
```

classifier versionはcurrent trial reportの`classifier_method_version`から取得し、空ならfail closedする。

current daily identity:

```text
schema_version = p8_daily_manifest.v2
method_version = p8_daily_manifest_builder.v2
classifier_version = current trial report classifier_method_version
p8_evidence_version = current trial report method_version
readiness_version = p9_readiness.v2
```

previous daily v2との比較は`compare_generation_identities(..., claim_component="classifier_version")`を使う。

source-head-only driftはWP2 contractどおりcomparableとする。

### 5.3 Cross-artifact cohort compatibility

daily v2とcumulative evidenceはartifact schemaが異なるため、primary schema equalityを要求しない。

cross-artifact compatibilityは次を明示的に検証する。

- program一致
- runtime_generation一致
- cumulative input status = provided
- cumulative run_id nonblank
- cumulative cutoffがcurrent cutoff以下
- cumulative cohort_countsにcurrent claim component cohortが存在するか
- cumulative automatic causal claimは別modern reportで0
- canonical link replacement=false

classifier claimのcohort存在判定は`cohort_counts`の次を使う。

```text
P|<runtime_generation>|classification|<current classifier version>
P|<runtime_generation>|proxy_trial_fact|<current classifier version>
```

cumulative manifest top-level declared classifier versionだけではcohort存在を証明しない。

宣言versionと実cohortが一致しない場合は次を記録する。

```text
declared_component_cohort_mismatch
```

これはidentity conflictとしてbundle生成を失敗させず、readinessを`collecting`へ留める不足証拠とする。

## 6. Required inputs

CLI required:

```text
--cycle-manifest
--trial-report
--trial-facts
--review-queue
--cumulative-manifest
--modern-attribution-report
--output-root
--runtime-generation
--source-head
--cutoff-utc
```

Optional:

```text
--previous-v2-manifest
--claim-scope
--frozen-validation
--replace-output
--stdout-json
```

### 6.1 Input validation

Required JSONはobjectでなければならない。

Required CSV:

`trial_facts`:

```text
trial_fact_id
event_timestamp_utc
operator_class
classifier_method_version
actual_episode_id
actual_link_confidence
evidence_tier
no_trade_flags
```

`review_queue`:

```text
review_item_id
question_type
evidence_tier
issue_flags
```

Required inputがmissing、unreadable、schema mismatchならoutputをpromoteしない。

absolute pathやraw rowsをerror/stdoutへ出さない。

## 7. WP5 daily manifest v2 contract

### 7.1 Output

`p8_daily_manifest_v2.json`は最低限次を持つ。

```text
schema_version
method_version
run_id
report_date
cutoff_utc
generation
operational_health
rolling_window
generation_comparison
daily_delta
review_queue_delta
actual_attribution_delta
semantic_token_status
cumulative_evidence_pointer
modern_attribution_pointer
issue_applicability
legacy_readiness_v1
p9_readiness_v2
meaningful_changes
input_sources
input_fingerprints
output_fingerprints
safety_boundary
```

### 7.2 Operational health

core stage names:

```text
candidate_slice
signal_context_slice
intraperiod_outcomes
p4
p5
p8
```

`operational_health.status=healthy`の必要条件:

- cycle manifest schema/method/report dateがnonblank
- core stage statusがすべて`ok`
- source.ohlcv_freshness=`valid`
- source interval=`15m`
- `no_automatic_tuning=true`
- trial report `ok=true`
- daily countsが非負整数
- required fingerprintsがnonblank

turning/macro auxiliary shadowのdisabledまたはfailedはcore healthをblockしない。warningとして別記する。

core failure、invalid input、identity conflictは`blocked_data`相当とし、CLIはinvalid inputとしてfail closedする。既存P8 failureを成功へ読み替えない。

### 7.3 Rolling window

legacy daily windowをそのまま記述する。

```text
report_date
window_min_timestamp
window_max_timestamp
counts
class_counts
side_counts
comparison
actual_evidence
review_queue_size
```

これはcumulative evidenceではないと明記する。

### 7.4 Stable current IDs

current accepted actual IDs:

```text
evidence_tier=actual_high_medium
actual_episode_id nonblank
actual_link_confidence in high|medium
```

sort・deduplicateする。

current review IDsはnonblank `review_item_id`をsort・deduplicateする。

exact duplicate rowはdeduplicate可能。同一IDでdaily-deltaに必要なselected fieldsが矛盾する場合はidentity conflictでfailする。

### 7.5 First v2 baseline

`--previous-v2-manifest`がない場合:

```text
generation_comparison.status = first_v2_baseline
review_queue_delta.new_items = []
review_queue_delta.backlog_items = current review IDs
review_queue_delta.resolved_items = []
review_queue_delta.expired_items = []
actual_attribution_delta.new_episode_ids = []
actual_attribution_delta.retained_episode_ids = current accepted actual IDs
actual_attribution_delta.lost_episode_ids = []
```

既存110件backlogを新規110件として扱わない。

backlog countだけではmeaningful anomalyを生成しない。

### 7.6 Comparable previous manifest

previous generationがcomparableの場合:

review queue:

```text
new = current - previous
backlog = current intersect previous
resolved = previous - current
expired = []
```

expiry metadataがないため自動でexpiredと推測しない。

actual attribution:

```text
new = current - previous
retained = current intersect previous
lost = previous - current
```

### 7.7 Baseline reset

previous generationがnot comparableまたはbaseline reset requiredの場合:

- count deltaを比較しない
- current queueはbacklogとして扱う
- new/resolved/lostは0
- generation comparison status/reasonを保存
- baseline_reset_required=true
- old/new generationを混ぜない

### 7.8 Semantic token status

trial fact `no_trade_flags`をshared operator semantics contractで正規化・分類する。

record:

```text
hard_tokens
advisory_tokens
unknown_tokens
rows_with_unknown_tokens
```

unknown tokenが1件以上ならmeaningful changeへ追加するが、classifier/gateを自動変更しない。

### 7.9 Cumulative pointer

record:

```text
logical_name
fingerprint
run_id
schema_version
method_version
cutoff_utc
program
runtime_generation
row_counts
cohort_counts
compatibility_status
missing_current_component_cohorts
```

absolute pathを保存しない。

### 7.10 ISSUE applicability

ISSUE-001 status priority:

1. generation baseline reset -> `not_comparable_generation_change`
2. `stop_rows=0` -> `not_applicable_no_stop_population`
3. `issue_001_qualified_rows>0` -> `applicable_evidence_present`
4. otherwise stop population present -> `applicable_no_qualified_rows`

`stop_rows=0`をresolvedとは呼ばない。

### 7.11 Meaningful changes

候補:

- new accepted actual episode
- lost accepted actual episode
- new review item
- resolved review item
- unknown semantic token
- generation baseline reset
- operational health failure
- cumulative evidence incompatibility
- P9 readiness state transition

backlog count単独はmeaningful changeではない。

これはnotification送信contractではない。mail/notificationを呼ばない。

## 8. WP6 P9 readiness v2 contract

### 8.1 Output

`p9_readiness_v2.json`:

```text
schema_version
method_version
state
dimensions
missing_requirements
claim_scope
legacy_readiness_v1
migration
production_ready
proposal_approval_status
safety_boundary
```

`production_ready`はこのpackageでは常にfalse。

`proposal_approval_status`はこのpackageでは常に`not_requested`。

### 8.2 Allowed state vocabulary

Full vocabulary:

```text
blocked_data
collecting
baseline_available
eligible_for_proposal
proposal_under_review
shadow_validating
human_approval_required
approved_for_bounded_implementation
accepted_shadow
approved_for_production
rejected
```

WP6 evaluatorが自動出力してよいのは次だけ。

```text
blocked_data
collecting
baseline_available
eligible_for_proposal
shadow_validating
human_approval_required
rejected
```

次はWP7/WP8のhuman decisionなしに出力してはならない。

```text
proposal_under_review
approved_for_bounded_implementation
accepted_shadow
approved_for_production
```

### 8.3 Dimensions

Required:

```text
operational_health
evidence_coverage
notification_usefulness
proposal_eligibility
adoption_readiness
```

各dimensionは最低限次を持つ。

```text
state
facts
missing_requirements
claim_scope
```

### 8.4 Claim scope

`--claim-scope`がない場合、current trial reportから次を作る。

```text
claim_id = current_manual_operator_classifier_generation
component_field = classifier_version
component_version = current classifier_method_version
required_segments = []
minimum_requirements = {}
threshold_status = not_frozen
```

これはperformance claimではなくcurrent generation cohortの識別だけである。

全A/B/C/STOP classをglobal requirementにしない。

side/regime/setup/class segmentはclaim scopeに明示された場合だけrequireする。

### 8.5 Legacy readiness

trial reportの既存`p9_readiness`をbyte-semanticに変更せず次へ保存する。

```text
legacy_readiness_v1
```

legacy 100/30または200/50はmigration説明用であり、v2 stateを直接決めない。

### 8.6 Operational-health dimension

healthyなら`baseline_available`、core failureなら`blocked_data`。

### 8.7 Evidence-coverage dimension

`blocked_data`:

- cumulative manifest invalid
- program/runtime mismatch
- cutoff future mismatch
- required cumulative fingerprints missing

`collecting`:

- cumulative baselineはあるがcurrent claim component cohortがない
- claim-required segmentがない
- actual-required claimでaccepted actual evidenceが0

`baseline_available`:

- compatible cumulative baselineあり
- current claim component cohortあり
- explicit claim-required segmentsを満たす
- actual-required claimならactual evidenceあり

current smokeではv4 classification/trial cohortがないため、このdimensionは`collecting`でなければならない。

### 8.8 Notification-usefulness dimension

`blocked_data`:

- report invalid
- automatic causal claims nonzero
- canonical link replacement true

`collecting`:

- validだがaccepted high/medium actualが0

`baseline_available`:

- accepted high/medium actualが1件以上
- automatic causal claims=0
- canonical replacement=false

proxy-only usefulnessをactual成功率と呼ばない。

### 8.9 Proposal-eligibility dimension

`collecting`:

- threshold_statusがnot_frozen
- minimum requirementsが空
- evidence coverageがcollecting

`eligible_for_proposal`:

- caller-provided claim scopeにexplicit minimum requirementsがある
- threshold_status=frozen_before_validation
- compatible evidenceで全minimumを満たす
- unresolved/no-OHLCVをperformance numeratorへ含めない
- actual-required claimはactual coverageを満たす

このstateはproposalを承認しない。

### 8.10 Adoption-readiness dimension

`collecting`:

- frozen validation inputなし

`shadow_validating`:

- frozen validation inputあり
- generation/cohort compatible
- calibration/validation time splitあり
- validation status=in_progress

`human_approval_required`:

- proposal eligible
- validation status=passed
- frozen versions/thresholdsがvalidation前に記録済み
- validation claim scope一致

`rejected`:

- validation status=rejectedまたはfailed

human approval recordをこのWP6で読まない。`human_approval_required`を超えない。

### 8.11 Top-level state priority

1. essential data blocked -> `blocked_data`
2. validation rejected/failed -> `rejected`
3. proposal eligible + validation passed -> `human_approval_required`
4. validation in progress -> `shadow_validating`
5. proposal requirements explicitly met -> `eligible_for_proposal`
6. compatible current-generation baseline and notification usefulness baseline -> `baseline_available`
7. otherwise -> `collecting`

current acceptance smoke expected state:

```text
collecting
```

Expected primary missing requirements:

```text
current classifier v4 cumulative classification cohort
current classifier v4 cumulative proxy_trial_fact cohort
frozen proposal thresholds
frozen validation cohort
```

global A/B/C/STOP absenceをmissing requirementへ自動追加しない。

## 9. Migration report

`p9_readiness_migration_report.md`は最低限次を説明する。

- legacy_readiness_v1 values
- p9_readiness_v2 state
- legacy thresholdはv2 decision thresholdではない
- daily windowとcumulative evidenceの分離
- current classifier v4対cumulative v1 cohort gap
- global all-four-class requirementを廃止しclaim-specificへ移行
- practical false固定を廃止しstate machineへ移行
- human approval前にproductionへ進まない
- no automatic tuning/order

## 10. Summary output

`p8_daily_summary_v2.md`は最低限次を説明する。

- daily rolling window facts
- operational health
- first baselineまたはprevious comparison status
- queue new/backlog/resolved/expired
- accepted actual new/retained/lost
- cumulative pointerとcohort gap
- semantic unknown token status
- ISSUE applicability
- legacy readiness v1
- readiness v2 stateと不足要件
- report-only shadow

## 11. Output transaction and determinism

Generate exactly four files:

```text
p8_daily_manifest_v2.json
p8_daily_summary_v2.md
p9_readiness_v2.json
p9_readiness_migration_report.md
```

Rules:

- all four filesをtemporary directoryで完成後atomic promote
- existing outputがあり`--replace-output`なしならexit 4
- replace failure時はprevious complete outputを保持
- partial outputを残さない
- current clockを内容へ含めない
- run_idはgeneration、cutoff、sorted input fingerprintsから決定
- sorted JSON keys
- UTF-8
- newline stable
- deterministic Markdown
- reportへabsolute path、raw row、account/order ID、secretを出さない

## 12. CLI

Create:

```text
tools/build_p8_daily_manifest_v2.py
```

Exit codes:

```text
0 success
2 missing/invalid input
3 identity conflict
4 output/I/O conflict
```

`--stdout-json`:

- exactly one JSON line
- no traceback
- no absolute path
- no raw row
- no private data

Compact success fields:

```text
ok
run_id
report_date
operational_health
comparison_status
queue_new
queue_backlog
queue_resolved
actual_new
actual_retained
actual_lost
readiness_v2_state
missing_requirements
output_files
```

## 13. Tests

### 13.1 Daily manifest tests

- operational health healthy contract
- core stage failure rejection
- auxiliary shadow failure does not block core
- first v2 baseline imports queue as backlog, new=0
- comparable previous queue new/backlog/resolved
- actual new/retained/lost
- generation reset suppresses deltas
- backlog-only is not meaningful change
- new actual is meaningful change
- unknown semantic token is meaningful change
- ISSUE no stop population is not applicable, not resolved
- deterministic run ID and bytes
- no absolute paths/raw rows
- identity conflict rejection
- atomic replace rollback

### 13.2 Readiness tests

- legacy readiness preserved separately
- daily-only count cannot satisfy cumulative evidence
- all four classes are not globally required
- current claim cohort missing -> collecting
- declared classifier v4 but only v1 cohorts -> declared_component_cohort_mismatch
- compatible current cohort -> baseline_available
- valid modern report with 58 accepted and zero causal claims -> usefulness baseline
- causal claim nonzero -> blocked_data
- canonical replacement true -> blocked_data
- no frozen thresholds -> proposal collecting
- explicit frozen requirements satisfied -> eligible_for_proposal only
- frozen validation in progress -> shadow_validating
- passed validation -> human_approval_required
- failed validation -> rejected
- never automatically output production/accepted states
- unresolved/no-OHLCV excluded from claim performance facts

### 13.3 CLI tests

- compact one-line success
- four files present
- missing input exit 2
- identity conflict exit 3
- existing output without replace exit 4
- deterministic replacement
- no traceback
- no absolute paths in stdout

## 14. Acceptance smoke

Run exactly one small report-only builder smoke. Do not rerun P8 daily cycle.

Inputs:

```text
cycle_manifest = logs/p8_operating_cycles/20260724/cycle_manifest.json
trial_report = logs/p8_operating_cycles/20260724/manual_operator_trial_evidence.json
trial_facts = logs/p8_operating_cycles/20260724/manual_operator_trial_facts.csv
review_queue = logs/p8_operating_cycles/20260724/manual_operator_trial_review_queue.csv
cumulative_manifest = local/reports/p_evidence/wp3_wp4_acceptance_20260725/latest/evidence_manifest.json
modern_attribution_report = local/reports/p_evidence/wp3_wp4_acceptance_20260725/latest/modern_attribution_report.json
output_root = local/reports/p8_daily_v2/wp5_wp6_acceptance_20260725
runtime_generation = Ver04-v5
source_head = 7024746f23251e32ff69cc63d72864a9af6ea446
cutoff_utc = 2026-07-25T01:05:00.785295Z
previous = omitted
claim scope = inferred current classifier generation
frozen validation = omitted
```

Acceptance:

```text
operational_health = healthy
comparison_status = first_v2_baseline
queue_new = 0
queue_backlog = 110
queue_resolved = 0
actual_new = 0
actual_retained = 2
actual_lost = 0
issue_001 = not_applicable_no_stop_population
legacy initial ready = false
legacy practical ready = false
readiness_v2 state = collecting
current classifier = manual_operator_classifier.v4
cumulative v4 classification cohort = missing
cumulative v4 proxy trial cohort = missing
notification usefulness accepted high/medium actual = 58
automatic causal claims = 0
canonical link replacement = false
production_ready = false
proposal_approval_status = not_requested
```

Generated artifactsはstage/commitしない。

## 15. Allowed files

```text
src/feedback/p8_daily_manifest_v2.py
src/feedback/p9_readiness_v2.py
tools/build_p8_daily_manifest_v2.py
tests/test_p8_daily_manifest_v2.py
tests/test_p9_readiness_v2.py
tests/test_build_p8_daily_manifest_v2_cli.py
chatgpt/specs/active/20260725_p_wp5_wp6_daily_manifest_and_p9_readiness_v2.md
```

## 16. Prohibited

- existing source modification
- existing P8 output modification
- cumulative artifact modification
- canonical CSV modification
- P8 cycle rerun
- full replay
- network
- dependency installation
- schedule/runtime/launchd/mail/notification modification
- gate/scoring/threshold/classifier change
- baseline adoption
- proposal approval
- production state
- automatic order
- reset, restore, checkout, clean, stash, push

## 17. Acceptance boundary

WP5/WP6 acceptanceはshadow daily manifestとreadiness evaluatorの受理だけを意味する。

次を認可しない。

- H2 cumulative baseline adoption
- H3 proposal threshold approval
- WP7 proposal decision
- WP8 source behavior change
- production apply
- notification/runtime wiring
