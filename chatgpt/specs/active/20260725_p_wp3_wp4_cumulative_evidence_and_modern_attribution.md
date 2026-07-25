---
title: "P WP3/WP4 Cumulative Evidence and Modern Attribution"
date: 2026-07-25
status: implementation-authorized
work_id: P-GENERATION-ALIGNMENT-WP3-WP4
program: P
packages: [WP3, WP4]
branch: Ver04-v5
reviewed_base: 3bb8c0853a718d270d802fa941f0ed7cef3fd2f1
safety_boundary: "report-only / derived inputs only / no canonical replacement / not FORMAL_GO / no automatic order / human decides manually"
---

# P WP3/WP4 — Cumulative Evidence Bank and Modern Attribution

## 1. Decision

WP0、WP1、WP2はacceptedである。WP3とWP4は正本計画のStep 3として一つのbounded implementationで実施する。

このpackageは、既存の派生済みP8・actual episode・v2 link・signal logを、世代分離された再構築可能な証拠bundleへ変換する。canonical input、production判断、通知、runtime、mail、gate、classifier、thresholdは変更しない。

このpackageで行わないこと:

- cumulative baselineの採用
- P9 readiness判断
- v2 linkのcanonical置換
- 新しいlink scoreまたはconfidence thresholdの導入
- 通知がactual entryを引き起こしたという自動因果主張
- private raw exchange exportの読取または出力への露出
- production apply

## 2. Verified baseline

2026-07-25時点の派生済み入力:

| input | verified rows | schema / method | verified SHA-256 |
|---|---:|---|---|
| `logs/csv/manual_trade_episodes.csv` | 149 | `manual_trade_episode.v1` | `7143975961cf25d862c41590b1ec2be586a921bee5e09e6f9e986fe8e56f9556` |
| `logs/csv/manual_trade_signal_links.csv` | 149 | `manual_trade_signal_link.v2` | `276c5d38cb4a4f71cb8cb72482beb0d334333e70868e39152a2ce8917def8c49` |
| `logs/csv/manual_operator_trial_facts_20260711.csv` | 364 | `manual_operator_trial_evidence.v1` | `2fa93692af9c2bf31ba55bec3d732ba262cb8c2149a754500042d60d503d16df` |
| `logs/csv/trades.csv` | 3182 | mixed historical signal log | `bb223978ed0b90d2861cd84609efd7aecfe55ae91a7354b5a1f2642e545c054a` |

`logs/csv/manual_operator_classifications.csv`はcurrent classification cohortの派生済み入力である。row countやfingerprintはrun時にmanifestへ記録する。

raw MEXC XLSXまたはprivate exportは入力に使わない。`manual_actual_*`の再importも行わない。actual証拠は既存の149 episode/linkを正本入力とする。

## 3. Source layout

新規source:

```text
src/feedback/p_cumulative_evidence.py
src/feedback/manual_trade_modern_attribution.py
tools/build_p_evidence_bundle.py
```

新規tests:

```text
tests/test_p_cumulative_evidence.py
tests/test_manual_trade_modern_attribution.py
tests/test_build_p_evidence_bundle_cli.py
```

既存WP2 contractを利用する:

```text
src/contracts/generation_identity.py
```

WP2 sourceは変更しない。

## 4. Shared rules

### 4.1 Standard library only

新規moduleとCLIはPython標準libraryだけで動作しなければならない。`pandas`、network、exchange API、current clock、git command、environment-derived current HEADへ依存しない。

### 4.2 Explicit generation

callerは次を明示する。

```text
program=P
runtime_generation=Ver04-v5
source_head=<accepted source commit>
schema_version=p_cumulative_evidence.v1
method_version=p_cumulative_evidence.v1
cutoff_utc=<timezone-aware ISO-8601>
classifier_version=<current classification version or legacy_unversioned>
linker_version=manual_trade_signal_link.v2
p8_evidence_version=manual_operator_trial_evidence.v1
```

`GenerationIdentity`でvalidateし、gitから暗黙取得しない。

### 4.3 Cutoff

- evidence event timestampが`cutoff_utc`より後ならfail closedする。
- timestampが必須のevidence kindで欠落・不正ならfailする。
- input fileのfilesystem mtimeはevidence cutoffとして使わない。
- provenance timestampは情報として保持できるが、event-time cutoffを置換しない。

### 4.4 Stable identity and conflicts

- evidence IDは`evidence_kind + authoritative source identity`から決定的に作る。
- 同一evidence ID・同一normalized payloadはexact duplicateとして1件へdeduplicateする。
- 同一evidence ID・異なるpayloadは`identity_conflict`でbundle生成を中止する。
- episode、link、classification、trial fact、decision eventを相互に同一IDとして扱わない。

### 4.5 Separation

最低限、次を別fieldで保持する。

```text
evidence_basis = proxy | actual | descriptive | human_confirmed
proxy_outcome
actual_episode_id
actual_link_confidence
actual_realized_pnl
human_basis = yes | no | unknown
causality_status = not_claimed | human_confirmed
```

- proxy rowへactual PnLをコピーしない。
- actual PnLをproxy TP/SL集計へ加算しない。
- human確認がない全自動生成rowは`human_basis=unknown`、`causality_status=not_claimed`。
- `human_confirmed`を自動生成しない。

### 4.6 Privacy and paths

manifest/reportへ記録してよいのはlogical input name、row count、schema、SHA-256だけである。absolute path、private export filename、account ID、order ID、raw input rowをJSON/Markdownへ露出しない。

## 5. WP3 cumulative evidence contract

### 5.1 Public constants

```python
EVIDENCE_SCHEMA_VERSION = "p_cumulative_evidence.v1"
EVIDENCE_METHOD_VERSION = "p_cumulative_evidence.v1"
EVIDENCE_MANIFEST_VERSION = "p_evidence_manifest.v1"
```

### 5.2 Required logical inputs

builderは明示されたPathから次を読む。

```text
classifications
trial_facts
episodes
links_v2
signal_log
```

optional:

```text
exact_observations
active_plan_candidates
signal_outcomes
```

required inputがmissing、unreadable、required identity fieldなしの場合はoutputをpromoteしない。

### 5.3 Evidence facts output

`evidence_facts.csv`の固定headers:

```text
schema_version
evidence_id
evidence_kind
source_identity
source_logical_name
event_timestamp_utc
signal_id
scenario_event_id
candidate_id
episode_id
link_id
side
setup_family
market_regime
operator_class
formal_execution_gate
notification_kind
operator_decision_state
proxy_outcome
actual_link_confidence
actual_realized_pnl
evidence_basis
human_basis
causality_status
component_version
runtime_generation
source_head
cohort_key
cutoff_utc
```

Required evidence kinds:

```text
classification
proxy_trial_fact
actual_episode
actual_link
decision_event
```

optional inputがある場合:

```text
exact_observation
active_plan_candidate
signal_outcome
```

Mapping requirements:

- classification identity: `classification_id`
- proxy trial identity: `trial_fact_id`
- actual episode identity: `episode_id`
- actual link identity: `link_id`
- decision event identity: nonblank `signal_id`
- exact observation identity: `observation_id`
- active plan candidate identity: `candidate_id`
- signal outcome identity: nonblank `signal_id`
- blank `signal_id` signal-log rowsはcountしてmanifestへ記録するが、decision evidence rowにはしない。
- classification component versionは`classifier_method_version`。
- trial fact component versionは`classifier_method_version`。
- episode component versionは`association_method_version`。
- link component versionは`link_method_version`。
- decision event component versionは`evaluation_trace_version`、空なら`legacy_unversioned`。
- exact observation component versionは`schema_version`、空なら`legacy_unversioned`。
- active plan candidate component versionは`active_plan_version`、次に`schema_version`、両方空なら`legacy_unversioned`。
- signal outcome component versionは`evaluation_trace_version`、次に`schema_version`、両方空なら`legacy_unversioned`。
- `cohort_key`はprogram、runtime generation、evidence kind、component versionを含む決定的な文字列。

### 5.4 Manifest

`evidence_manifest.json`は最低限次を持つ。

```text
schema_version
method_version
run_id
generation
cutoff_utc
input_sources
input_status
row_counts
exact_duplicate_counts
blank_identity_counts
cohort_counts
evidence_basis_counts
actual_link_confidence_counts
output_fingerprints
safety_boundary
```

- `run_id`はgeneration、cutoff、sorted input fingerprintsから決定的に作る。
- current timeを含めない。
- `output_fingerprints`はmanifest自身を除く出力のSHA-256を持つ。
- JSONはsort keys、UTF-8、末尾改行でdeterministicにする。

### 5.5 Summary

`evidence_summary.md`は最低限次を明示する。

- full-period evidenceでありdaily 5-day healthではない
- actual episode/link 149 baseline count
- classification/trial fact/decision row coverage
- proxy / actual / descriptive separation
- cohort別件数
- high/medium/low/ambiguous link別件数
- cutoffとinput fingerprints
- baseline candidate only; H2 human adoption not recorded
- report-only / not FORMAL_GO / no automatic order

### 5.6 History and latest

CLI output rootの下に次を生成する。

```text
history/<run_id>/evidence_manifest.json
history/<run_id>/evidence_facts.csv
history/<run_id>/evidence_summary.md
history/<run_id>/modern_link_candidates_v3.csv
history/<run_id>/notification_usefulness_ledger.csv
history/<run_id>/modern_attribution_review_queue.csv
history/<run_id>/modern_attribution_report.json
history/<run_id>/modern_attribution_report.md
latest/<same eight files>
```

- history directoryはimmutable。既存同run_idのbytesが完全一致ならidempotent success。
- 同run_idでbytesが異なる場合は`history_identity_conflict`。
- latestはstage directoryで全出力を完成後、bundle単位で置換する。
- failure時にpartial latestを残さない。

## 6. WP4 modern attribution contract

### 6.1 Scope

WP4はv2 linkを再採点・再選択しない。v2のepisode/link/signal relationをbaselineとして保存し、現行signal metadataでoffline enrichmentとcoverage評価を行う。

これは`manual_trade_signal_link.v3`のproduction replacementではなく、次のcandidate schemaである。

```python
MODERN_ATTRIBUTION_SCHEMA_VERSION = "manual_trade_modern_attribution.v1"
MODERN_LINK_CANDIDATE_VERSION = "manual_trade_signal_attribution_candidate.v3"
```

### 6.2 Modern metadata lookup

signal logは`signal_id`でindexする。selected metadata:

```text
was_notified
notify_reason_codes
reason_for_notification
summary_variant
advice_variant
trade_execution_gate
trade_execution_blockers
active_primary_action
side_aware_primary_side
side_aware_primary_class
side_aware_primary_state
structural_priority_side
structural_alignment_state
operator_decision_state
operator_decision_primary_side
followup_for_signal_id
```

- optional columnsは欠落可能。
- 同一signal_idのselected metadataが同一ならdeduplicateする。
- 同一signal_idでselected nonblank metadataが矛盾する場合は`signal_identity_conflict`。
- metadataを補完するためAI/news textを解釈しない。

`notification_kind`は次のfieldの最初のnonblank値をそのまま使用する。

```text
signal metadata `notification_kind`
signal metadata `summary_variant`
signal metadata `reason_for_notification`
baseline v2 link `notification_class`
```

値の意味を推測して書き換えない。

同一signalに複数classificationまたはtrial factがある場合、`p5_operator_classes`と`proxy_outcomes`は全nonblank値をsort・deduplicateして保存する。最後の1rowで上書きしない。

### 6.3 Candidate output

`modern_link_candidates_v3.csv`はv2 link 1 rowにつき1 rowを保持する。

Required fields:

```text
schema_version
candidate_id
baseline_link_id
episode_id
signal_id
baseline_link_status
baseline_link_confidence
baseline_link_reason
reason_bucket
candidate_relation
notification_kind
was_notified
notify_reason_codes
operator_decision_state
operator_primary_side
formal_execution_gate
formal_blockers
active_primary_action
side_aware_primary_class
side_aware_primary_state
structural_priority_side
structural_alignment_state
modern_metadata_status
human_basis
causality_status
```

`candidate_relation`:

```text
preserved_v2_link
preserved_v2_ambiguous
preserved_v2_no_candidate
```

reason bucket priority:

1. `side_conflict`
2. `symbol_conflict`
3. v2 reason `competing_candidate_tie` -> `ambiguous_tie`
4. followup/management reason -> `followup_only`
5. no signal or no candidate -> `no_candidate`
6. linked high -> `linked_high`
7. linked medium -> `linked_medium`
8. linked low -> `linked_low`
9. linked ambiguous -> `ambiguous_tie`
10. otherwise `multiple_signal_candidates`

`missing_modern_metadata`はlink reason bucketを置換せず、`modern_metadata_status=missing|partial|complete`で表す。

### 6.4 Usefulness ledger

`notification_usefulness_ledger.csv`はactual episode-centric rowsとnotification/signal-centric rowsを区別する。

Required fields:

```text
schema_version
ledger_id
ledger_basis
signal_id
episode_id
notification_kind
was_notified
notify_reason_codes
operator_decision_state
operator_primary_side
formal_execution_gate
formal_blockers
p5_operator_classes
active_primary_action
side_aware_primary_class
side_aware_primary_state
structural_priority_side
structural_alignment_state
proxy_outcomes
actual_link_confidence
actual_position_side
entry_latency_minutes
actual_realized_pnl
usefulness_category
human_basis
causality_status
```

`ledger_basis`:

```text
actual_episode
notification_without_accepted_actual
```

Accepted actual attribution for descriptive aggregation is v2 `link_status=linked` and confidence `high|medium` only。low/ambiguousはactual usefulnessの分子へ入れない。

- `entry_latency_minutes`はbaseline v2 linkの`time_delta_minutes`をそのまま保持する。
- low/ambiguous/no-candidate episode rowはactual episodeの記述としてPnLを保持してよいが、`accepted_high_medium`、accepted actual PnL row count、accepted actual PnL aggregateへ入れない。
- positive proxy evidenceには少なくとも`resolved_positive`、`positive`、`win`、`favorable`、`success`を含める。値をactual successとは呼ばない。

Conservative usefulness category rules:

1. actual high/medium + followup/management notification -> `management_useful`
2. actual high/medium + formal gate `pass` -> `formal_candidate_used`
3. actual high/medium + operator state `check_15m` or P5 contains `B_CHECK_15M` -> `chart_check_then_entry`
4. actual high/medium + operator state `watch_zone` or P5 contains `C_WATCH_ZONE` -> `chart_check_then_entry`
5. actual high/medium + notification kind explicitly contains `attention` -> `attention_then_entry`
6. actual high/medium but above evidence absent -> `ambiguous`
7. notified signal without accepted actual and positive proxy evidence -> `useful_no_entry_proxy`
8. notified signal without accepted actual -> `no_actual_action`
9. low/ambiguous/no-candidate actual link -> `ambiguous`

- `ignored_or_unrelated`はhuman basisが`no`と入力された将来rowだけであり、この自動runでは生成しない。
- actual rowの`proxy_outcomes`は説明用に別fieldへ置けるが、actual PnLと集計しない。
- signal-only rowの`actual_realized_pnl`は空。
- 全自動rowは`human_basis=unknown`, `causality_status=not_claimed`。

### 6.5 Review queue

`modern_attribution_review_queue.csv`は例外だけを含む。

Question types:

```text
low_or_ambiguous_link
missing_modern_metadata
human_basis_for_high_medium_actual
signal_identity_issue
```

- high/medium actualでusefulness categoryが`formal_candidate_used|chart_check_then_entry|attention_then_entry|management_useful`になったrowだけ、human basis確認候補にできる。
- 全149件を無条件にqueueへ入れない。
- low/ambiguous/no-candidateはreason付きでqueue化する。
- queueはcanonical linkを変更しない。

### 6.6 Reports

`modern_attribution_report.json`と`.md`は最低限次を分離する。

```text
baseline_episodes
baseline_links
reason_bucket_counts
confidence_counts
modern_metadata_coverage
actual_attribution
proxy_only_usefulness
notification_kind_breakdown
operator_state_breakdown
review_queue_counts
causality_statement
safety_boundary
```

- 149 -> reason/confidence flowを説明する。
- daily eligible countはinputに存在する場合だけ別fieldで表示し、full-period countと混ぜない。
- actual PnL summaryとproxy outcome summaryを別sectionにする。
- automatic causal claimは常に0件。
- v2 canonical replacementはfalse。

## 7. CLI contract

`tools/build_p_evidence_bundle.py`は1 commandでWP3とWP4を生成する。

Required args:

```text
--classifications
--trial-facts
--episodes
--links-v2
--signal-log
--output-root
--runtime-generation
--source-head
--cutoff-utc
```

Optional args:

```text
--exact-observations
--active-plan-candidates
--signal-outcomes
--stdout-json
```

- success exit 0
- invalid/missing input exit 2
- identity conflict exit 3
- output/history conflict or I/O failure exit 4
- `--stdout-json`は1行JSONだけをstdoutへ出す。
- stdoutへabsolute paths、raw rows、secretsを出さない。
- output root外へ書かない。
- dry-runは必須ではない。実装する場合はoutputを書かない。

## 8. Tests

### 8.1 Cumulative evidence tests

- deterministic row order and bytes
- explicit generation validation
- cutoff enforcement
- exact duplicate exclusion
- identity conflict rejection
- proxy/actual/descriptive separation
- no actual PnL copied to proxy rows
- cohort separation for classifier v1/v4
- blank signal identity count without decision row
- manifest logical paths only
- input/output fingerprints
- history idempotence
- history same-ID conflict
- atomic latest rollback

### 8.2 Modern attribution tests

- preserves v2 link identity and selected signal
- all reason-bucket mappings
- high/medium accepted actual only
- low/ambiguous excluded from actual usefulness numerator
- formal/check-15m/watch/attention/management categories
- signal-only useful proxy versus no actual action
- actual/proxy monetary separation
- modern metadata missing/partial/complete
- signal identity conflict
- no automatic human confirmation or causality claim
- exception-only queue
- deterministic outputs

### 8.3 CLI test

- compact success JSON
- missing input exit 2
- no traceback
- no absolute path in stdout
- all eight expected files under history and latest

## 9. Acceptance smoke

After unit tests, run exactly one report-only smoke against these existing derived inputs:

```text
classifications = logs/csv/manual_operator_classifications.csv
trial_facts = logs/csv/manual_operator_trial_facts_20260711.csv
episodes = logs/csv/manual_trade_episodes.csv
links_v2 = logs/csv/manual_trade_signal_links.csv
signal_log = logs/csv/trades.csv
output_root = local/reports/p_evidence/wp3_wp4_acceptance_20260725
runtime_generation = Ver04-v5
source_head = 3bb8c0853a718d270d802fa941f0ed7cef3fd2f1
cutoff_utc = 2026-07-25T01:05:00.785295Z
```

最初のsmokeは`2026-07-25T00:00:00Z`でfail-closedし、`trades.csv`末尾の`2026-07-25T01:05:00.785295Z`を正しく拒否した。FIX1では原因を変更したため、上記の実データ終端cutoffでsmokeをexactly one rerunしてよい。cutoffを実データ終端より後へ広げない。

Do not use raw XLSX, `manual_actual_*`, network, runtime, mail, or notification commands.

Smoke acceptance:

- episode rows = 149
- v2 link rows = 149
- one deterministic run bundle only
- no canonical input modified
- output under local report root only
- no artifact committed
- manifest/report explain full-period versus daily distinction
- actual/proxy separate
- causality not claimed

Do not rerun the same smoke merely to collect another health signal. Unit tests may verify determinism with fixtures; actual smoke is once.

## 10. Allowed implementation files

```text
src/feedback/p_cumulative_evidence.py
src/feedback/manual_trade_modern_attribution.py
tools/build_p_evidence_bundle.py
tests/test_p_cumulative_evidence.py
tests/test_manual_trade_modern_attribution.py
tests/test_build_p_evidence_bundle_cli.py
chatgpt/specs/active/20260725_p_wp3_wp4_cumulative_evidence_and_modern_attribution.md
```

No existing source file should require modification. If integration requires changing an existing production/P8 module, stop and report blocked.

## 11. Prohibited

- `main.py`
- execution/observation/opportunity gates
- classifier, scoring, threshold, semantic token changes
- current P8 operating-cycle source
- current P9/readiness source
- notification trigger, mail, runtime, launchd
- canonical CSV overwrite
- raw exchange export or XLSX read
- `paper_positions.csv` integration
- production adoption
- automatic baseline adoption
- automatic proposal selection
- automatic order
- full replay or repeated actual smoke
- dependency installation
- broad cleanup
- reset, restore, checkout, clean, stash, push

## 12. Acceptance

WP3/WP4は次を満たす時だけaccepted候補となる。

1. generation・cutoff・source fingerprintsを持つ。
2. version cohortを混ぜない。
3. stable identityとconflict detectionがある。
4. proxy、actual、descriptive、human-confirmedを分離する。
5. 149 episode/linkをfull-period baselineとして説明できる。
6. modern metadata coverageとv2 reason/confidence flowを説明できる。
7. v2 link relationを変更しない。
8. high/mediumだけをaccepted actual attributionとして記述集計する。
9. actual PnLとproxy outcomeを混ぜない。
10. causalityを自動主張しない。
11. exception-only review queueを作る。
12. deterministic history/latest outputを作る。
13. canonical inputs、production behavior、notification、runtimeを変更しない。
14. cumulative baseline adoption、P9 readiness、proposal approvalは未実施と明記する。
15. local commitを作成しpushしない。

## 13. Post-package boundary

WP3/WP4 acceptanceはevidence bundleとmodern attribution candidateの受理だけを意味する。

次を自動認可しない。

- H2 cumulative baseline adoption
- WP5 daily manifest v2 connection
- WP6 P9 readiness v2 thresholds
- WP7 proposal approval
- WP8 source behavior change
- production apply
