---
title: "BTC Monitor P評価基盤 実用運用接続・通知有用性再定義計画書"
date: 2026-07-25
tags:
  - btc-monitor
  - p-plan
  - p8
  - p9
  - notification-usefulness
  - cumulative-evidence
  - generation-alignment
  - execution-gate
  - report-only
status: implementation-ready
work_id: P-OPERATIONAL-COMPLETION-1
target_branch: Ver04-v5
base_head: a8431901dcba9daf60efe2f7675fd0585f24cf1d
safety_boundary: "report-only / no production gate change / no notification behavior change / no runtime apply / no automatic order / human decides manually"
---

> [!abstract]
> P世代整合パッケージWP0〜WP8により、世代識別、累積証拠、P8 daily manifest v2、P9 readiness v2、actual/proxy分離、安全境界は実装された。
>
> ただし、現在はacceptance用の単発生成に留まり、日次運用へ自動接続されていない。また、`accepted_high_medium_actual=58`は「通知が役立った58件」ではなく、high/medium confidenceでsignalとactual tradeが関連付いた58件である。さらに、classifier v4のadvisory tokenと現行formal execution gateの一律blockには意味の差が残る。
>
> 本計画では、**通知関連付けと人間有用性を再定義し、current-generation累積証拠とP8/P9 v2を既存の日次runnerへ接続し、formal gate差分をcounterfactual reportとして測定する**。
>
> 今回許可するのはreport-only実装までである。`execution_gate.py`、Phase1、通知trigger、threshold、classifier、runtime、launchd、mail、注文挙動は変更しない。production gate変更は、本計画の証拠を人間が確認した後の別TASKとする。

## 📋 目次

- [1. 結論と実装許可範囲](#1-結論と実装許可範囲)
- [2. 確認済みの未完了点](#2-確認済みの未完了点)
- [3. 今回の目標状態](#3-今回の目標状態)
- [4. 対象外](#4-対象外)
- [5. 目標データフロー](#5-目標データフロー)
- [6. 通知有用性v2契約](#6-通知有用性v2契約)
- [7. current-generation累積証拠契約](#7-current-generation累積証拠契約)
- [8. P9 readiness品質契約](#8-p9-readiness品質契約)
- [9. formal gate意味差分レポート](#9-formal-gate意味差分レポート)
- [10. 日次runner接続契約](#10-日次runner接続契約)
- [11. 実施パッケージ](#11-実施パッケージ)
- [12. 変更対象ファイル](#12-変更対象ファイル)
- [13. 出力配置](#13-出力配置)
- [14. テスト計画](#14-テスト計画)
- [15. Acceptance run](#15-acceptance-run)
- [16. 完了条件](#16-完了条件)
- [17. 停止条件](#17-停止条件)
- [18. 人間承認境界](#18-人間承認境界)
- [19. Commit方針](#19-commit方針)

---

## 1. 結論と実装許可範囲

今回の実装は、次の4点を一度に完了させる。

| 項目 | 今回の対応 | production挙動 |
|---|---|---|
| 通知有用性 | associationとnotification usefulnessを分離 | 不変 |
| v4累積証拠 | 日次P8出力から自動再構築 | 不変 |
| P8/P9 v2 | 既存daily runnerへ接続 | 不変 |
| formal gate矛盾 | counterfactual reportで影響測定 | gate自体は不変 |

今回のTASK終了時点では、次を正しい状態とする。

```text
P8 core daily cycle: existing behavior unchanged
P current-generation evidence: automatically refreshed after successful P8 cycle
P8 daily manifest v2: generated for each successful daily cycle
P9 readiness v2: recalculated from current evidence
notification usefulness: descriptive association and human-confirmed usefulness are separate
formal gate advisory/hard difference: measured only, not applied
production_ready: false
proposal_approval_status: not_requested
```

> [!warning]
> `src/trade/execution_gate.py`の`if no_trade_flags:`は今回変更しない。
>
> advisory tokenをproduction gateから除外する変更は、counterfactual結果、false positive/negative、人間判断を確認した後の別TASKでのみ許可する。

---

## 2. 確認済みの未完了点

### 2.1 通知有用性の名称と実体が一致していない

現在の`accepted_high_medium_actual=58`は、次の条件で数えられている。

```text
actual link status = linked
actual link confidence = high or medium
```

`was_notified=true`は必須ではない。そのため、58件を通知有用性として扱ってはならない。

### 2.2 metadata completenessが不足している

確認済みの現状は次のとおり。

| 項目 | 件数 |
|---|---:|
| actual episode/link | 149 |
| accepted high/medium association | 58 |
| modern metadata missing | 53 |
| modern metadata partial | 96 |
| modern metadata complete | 0 |
| operator decision state blank | 149 |

この状態では、人間に役立ったことを実証したとは扱わない。

### 2.3 current v4累積cohortが存在しない

現在のP8/P9 v2は次を検出している。

```text
current classifier = manual_operator_classifier.v4
cumulative classification cohort = manual_operator_classifier.v1
cumulative proxy-trial cohort = manual_operator_classifier.v1
```

日次outputにはv4 classification/trial factsがあるが、current-generation累積証拠へ自動集約されていない。

### 2.4 P8/P9 v2はacceptance用の単発生成

`tools/build_p_evidence_bundle.py`と`tools/build_p8_daily_manifest_v2.py`は存在するが、`tools/run_p8_daily_cycle.py`から呼ばれていない。

### 2.5 source headが手入力

`--source-head`がrequired argumentであり、古いHEADを渡したacceptance artifactが残っている。生成時のbuilder sourceを自動解決し、手入力による誤記を防止する必要がある。

### 2.6 formal gateの意味差が未測定

classifier v4ではadvisory tokenをC/WATCH側へ扱える一方、formal gateはnon-empty `no_trade_flags`を一律blockする。

ただし、`phase1_inactive`や`setup_not_ready`など他blockerも多いため、advisoryだけを除外しても実際に何件のgate結果が変わるかは未測定である。

---

## 3. 今回の目標状態

### 3.1 評価上の正しい分離

次を別の事実として保持する。

| 事実 | 意味 |
|---|---|
| accepted actual association | signalとactual tradeがhigh/medium confidenceで関連付いた |
| notified accepted actual | accepted associationのうち、対応signalが実際に通知された |
| descriptive notification usefulness | 通知後にentry等が観測されたが、因果は主張しない |
| human-confirmed usefulness | 人間が通知の役立ち方を確認した |
| proxy usefulness | actual entryを伴わないproxy評価 |
| formal execution eligibility | production formal gateが許可したか |

### 3.2 日次運用上の正しい連動

既存daily runnerの成功後に、同じprocess内で次を順番に実行する。

```text
1. existing P8 operating cycle
2. current-generation cumulative evidence refresh
3. formal gate semantic impact report generation
4. P8 daily manifest v2 generation
5. P9 readiness v2 generation
6. consolidated status write
```

### 3.3 安全性

- P8 core生成結果は既存と同じ。
- notification decision、送信、subject、recipient、cooldown、重複抑止は変更しない。
- `execution_gate.py`を変更しない。
- Phase1 activationを変更しない。
- thresholdを追加・緩和しない。
- classifier判定を変更しない。
- runtime/launchd/mailを変更しない。
- automatic orderを追加しない。

---

## 4. 対象外

今回、次は実施しない。

1. advisory tokenをformal gateから除外するproduction変更
2. Phase1 `watch`をactiveへ変更すること
3. A/B/C/STOP taxonomyの変更
4. notification trigger、kind、頻度、cooldown、suppressionの変更
5. claim threshold値の決定
6. frozen validationの承認
7. canonical actual linkの置換
8. human basisの自動推測
9. PnLから因果を主張すること
10. FORMAL_GOまたは自動注文
11. launchd plistの変更・reload
12. SMTPまたは実通知テスト

---

## 5. 目標データフロー

```text
logs/p8_operating_cycles/YYYYMMDD/
  cycle_manifest.json
  manual_operator_classifications.csv
  manual_operator_trial_facts.csv
  manual_operator_trial_review_queue.csv
  ...
          |
          | deterministic scan of accepted daily directories
          v
local/reports/p_evidence/p_current_generation/
  history/<run_id>/
  latest/
    evidence_manifest.json
    evidence_facts.csv
    evidence_summary.md
    modern_link_candidates_v3.csv
    notification_usefulness_ledger.csv
    modern_attribution_review_queue.csv
    modern_attribution_report.json
    modern_attribution_report.md
    formal_gate_semantic_impact.json
    formal_gate_semantic_impact.md
          |
          v
logs/p8_operating_cycles/YYYYMMDD/p8_v2/
  p8_daily_manifest_v2.json
  p8_daily_summary_v2.md
  p9_readiness_v2.json
  p9_readiness_migration_report.md
```

### 5.1 accepted daily directory

累積対象へ含める日次directoryは、最低限次を満たすこと。

```text
name = YYYYMMDD
cycle_manifest.json exists
cycle manifest reports successful core stages
manual_operator_classifications.csv exists
manual_operator_trial_facts.csv exists
all accepted row timestamps <= cutoff_utc
```

不完全なdirectoryは黙って混ぜず、manifest warningへ記録する。現在日のcore outputが不完全ならrefreshを失敗させる。

### 5.2 cutoff

wall clockをrun identityへ使用しない。

`cutoff_utc`は、成功したcurrent cycleの`cycle_manifest.source.max_timestamp`をUTCへ正規化した値を使用する。

同じ入力、同じsource commit、同じcutoffなら同一run IDと同一bytesを生成する。

### 5.3 source head

CLI利用者が任意文字列を入力する方式を廃止する。

- `--source-head`はoptional overrideとする。
- 未指定時はrepo rootで`git rev-parse HEAD`を1回だけ実行する。
- 40桁hexでなければcompact errorで停止する。
- manifestには`source_head_resolution=git`または`explicit_override`を記録する。
- acceptance runはoverrideを使用せず、自動取得を使用する。

---

## 6. 通知有用性v2契約

### 6.1 既存値の改名

次の曖昧な名称を、意味が明確な名称へ変更する。

```text
accepted_high_medium_actual
  -> accepted_high_medium_actual_associations
```

旧fieldは互換用aliasとして1世代のみ残してよいが、summaryとP9新判定では使用しない。aliasを残す場合は`deprecated_aliases`へ明示する。

### 6.2 notified accepted actual

次をすべて満たすrowだけを数える。

```text
ledger_basis = actual_episode
baseline link status = linked
actual_link_confidence in {high, medium}
was_notified = true
```

field名:

```text
notified_accepted_actual_associations
```

### 6.3 通知なしassociation

```text
not_notified_accepted_actual_associations
```

`was_notified`がblank/unknownの場合は通知なしへ混ぜず、次へ分離する。

```text
unknown_notification_status_accepted_actual_associations
```

### 6.4 usefulness category

acceptedかつnotifiedのrowだけについて、次を集計する。

```text
formal_candidate_used
chart_check_then_entry
attention_then_entry
management_useful
ambiguous
```

actualとproxyは別集計とし、`notification_without_accepted_actual`をactual usefulnessへ含めない。

### 6.5 human-confirmed usefulness

`human_basis`が`unknown`またはblankでないrowのみhuman-confirmedとして数える。

```text
human_confirmed_usefulness_count
human_unconfirmed_usefulness_count
```

自動で`human_basis`を埋めてはならない。

### 6.6 metadata coverage

次をactual association母集団とnotified accepted母集団の両方で出す。

```text
missing
partial
complete
```

### 6.7 direction comparison

明示的なoperator sideが`long`または`short`の場合のみactual position sideと比較する。

比較sideの優先順位:

```text
operator_primary_side
```

他fieldから推測しない。

出力:

```text
operator_direction_match
operator_direction_mismatch
operator_direction_unknown
operator_direction_match_rate
```

rateの分母はmatch+mismatchのみ。分母0なら`null`とする。

### 6.8 latencyとPnL

notified accepted actualについて、値が存在する場合だけ次を記録する。

```text
entry_latency_count
entry_latency_median_minutes
entry_latency_p90_minutes
realized_pnl_count
realized_pnl_sum
realized_pnl_median
positive_pnl_count
negative_pnl_count
zero_pnl_count
```

これらはdescriptiveであり、因果または自動採用を意味しない。

### 6.9 causality boundary

全出力に次を維持する。

```text
automatic_causal_claims = 0
causality_status = not_claimed
canonical_link_replacement = false
```

---

## 7. current-generation累積証拠契約

### 7.1 日次outputの自動集約

新しいorchestratorを追加し、`logs/p8_operating_cycles/`配下のaccepted daily directoriesを日付順に走査する。

推奨CLI:

```text
tools/refresh_p_current_evidence.py
```

必須入力はrepo内の既定pathを持ち、テスト用overrideのみ許可する。

### 7.2 集約対象

- `manual_operator_classifications.csv`
- `manual_operator_trial_facts.csv`
- `logs/csv/manual_trade_episodes.csv`
- `logs/csv/manual_trade_signal_links.csv`
- `logs/csv/trades.csv`

任意入力が存在する場合のみ、既存contractに従って含める。

- exact observations
- active plan candidates
- signal outcomes

### 7.3 世代分離

各rowのcomponent versionを保持し、v1とv4を同じcohortへ合算しない。

```text
P|Ver04-v5|classification|manual_operator_classifier.v1
P|Ver04-v5|classification|manual_operator_classifier.v4
P|Ver04-v5|proxy_trial_fact|manual_operator_classifier.v1
P|Ver04-v5|proxy_trial_fact|manual_operator_classifier.v4
```

P9 current coverageはv4だけを見る。

### 7.4 重複とconflict

- 同一identity・同一payloadはdedupeする。
- 同一identity・異なるpayloadはfail closedする。
- per-source fingerprintをmanifestへ記録する。
- aggregate fingerprintだけで個別lineageを失わない。
- absolute pathはoutputへ記録しない。

### 7.5 delta-onlyの意味

毎日全source fileを再走査してもよいが、生成結果はcontent-addressedでなければならない。

新しい入力がなければ同じrun ID・同じbytesとなり、historyを増やさない。

---

## 8. P9 readiness品質契約

### 8.1 dimension分離

既存の`notification_usefulness`を次の2つへ分離する。

```text
actual_association_coverage
notification_usefulness
```

#### actual_association_coverage

high/medium actual associationが存在すればdescriptive baselineを持てる。

#### notification_usefulness

最低限、notified accepted actualが存在することを要求する。ただしhuman-confirmedが0の場合は「人間有用性が実証済み」とは扱わない。

factsには次を含める。

```text
accepted_high_medium_actual_associations
notified_accepted_actual_associations
unknown_notification_status_accepted_actual_associations
human_confirmed_usefulness_count
metadata_complete_notified_actual_count
operator_direction_match_rate
ambiguous_notified_actual_rate
```

### 8.2 state

```text
blocked_data
collecting
baseline_available
eligible_for_proposal
shadow_validating
human_approval_required
rejected
```

notification usefulnessのstateは次とする。

| 条件 | state |
|---|---|
| report欠落、causal claimあり、canonical replacementあり | blocked_data |
| notified accepted actual = 0 | collecting |
| notified accepted actual > 0、human-confirmed = 0 | baseline_available |
| human-confirmed > 0 | baseline_available |

`baseline_available`はdescriptive baselineであり、production-readyではない。

### 8.3 quality minimum requirements

threshold値は実装側で決めない。claim scopeから明示的に渡された場合だけ評価する。

新たに対応するflat key:

```text
accepted_actual_associations_min
notified_accepted_actual_min
human_confirmed_usefulness_min
metadata_complete_notified_actual_min
operator_direction_match_rate_min
ambiguous_notified_actual_rate_max
```

既存keyは互換維持する。

```text
classification_cohort_rows_min
proxy_trial_fact_cohort_rows_min
```

検証規則:

- countは0以上のint。
- rateは0以上1以下のfinite number。
- boolを数値として受理しない。
- 分母0でrateが`null`の場合、requirementは未達。
- unsupported keyはfail closed。
- threshold statusが`frozen_before_validation`でなければeligibleにしない。
- minimum requirementsが空ならeligibleにしない。

### 8.4 production boundary

次は常に維持する。

```text
production_ready = false
proposal_approval_status = not_requested
```

人間承認を表す入力が将来追加されるまでは変更しない。

---

## 9. formal gate意味差分レポート

### 9.1 目的

production codeを変更せず、次の2条件を同じhistorical/current rowsへ適用して差分を測る。

```text
current rule:
  non-empty no_trade_flags => no_trade_flags_present blocker

counterfactual rule:
  hard or unknown token => blocker
  advisory-only token => no no_trade blocker
```

### 9.2 shared semantic contract

`src/contracts/operator_semantics.py`のhard/advisory/unknown分類を使用する。独自token listを複製しない。

### 9.3 必須集計

```text
total_rows
rows_with_no_trade_flags
advisory_only_rows
hard_token_rows
unknown_token_rows
mixed_hard_advisory_rows
current_no_trade_blocked_rows
counterfactual_no_trade_blocked_rows
rows_where_no_trade_blocker_would_be_removed
rows_still_blocked_by_other_formal_reasons
rows_potentially_changed_to_pass
```

### 9.4 breakdown

可能なfieldがある場合だけ次で分解する。

- side
- operator class
- notification kind
- formal execution gate
- actual link confidence
- actual position side

### 9.5 safety interpretation

`rows_where_no_trade_blocker_would_be_removed`を、そのまま「entry可能件数」と表現しない。

他blockerが残る場合は`rows_still_blocked_by_other_formal_reasons`へ入れる。

`rows_potentially_changed_to_pass`が0件でも、意味契約の不一致が解消済みとは扱わない。

### 9.6 output

```text
formal_gate_semantic_impact.json
formal_gate_semantic_impact.md
```

必須文言:

```text
counterfactual only
execution_gate.py unchanged
no production authorization
human approval required before any gate change
```

---

## 10. 日次runner接続契約

### 10.1 接続先

`tools/run_p8_daily_cycle.py`へreport-only後続stageを追加する。

既存の`run-p8-operating-cycle`commandと引数は変更しない。

### 10.2 実行順序

core cycle成功後のみ次を実行する。

1. current evidence refresh
2. P8/P9 v2 build

formal gate impactはevidence refresh内で生成する。

### 10.3 previous manifest

前日差分用のprevious manifestは、current dateより前の日付directoryから最新の成功済み

```text
p8_v2/p8_daily_manifest_v2.json
```

を選ぶ。

同日再実行では、同日の既存manifestをpreviousとして使用しない。

### 10.4 failure semantics

| 状況 | status | return code |
|---|---|---:|
| core P8失敗 | failed | core code |
| core成功、evidence refresh失敗 | partial_failure | 非0 |
| evidence成功、P8/P9 v2失敗 | partial_failure | 非0 |
| 全成功 | success | 0 |

core outputを削除・rollbackしない。ただしstatusに後続stage失敗を明示する。

### 10.5 status payload

`logs/runtime/p8_daily_cycle_last_result.json`へ追加する。

```text
evidence_refresh.status
evidence_refresh.run_id
evidence_refresh.latest_manifest_path
evidence_refresh.current_v4_classification_rows
evidence_refresh.current_v4_proxy_trial_rows
formal_gate_semantic_impact.status
formal_gate_semantic_impact.rows_where_no_trade_blocker_would_be_removed
formal_gate_semantic_impact.rows_potentially_changed_to_pass
p8_v2.status
p8_v2.run_id
p8_v2.manifest_path
p8_v2.readiness_state
p8_v2.missing_requirements
```

absolute path、raw trade row、account/order/fill IDをstatusへ含めない。

### 10.6 dry-run

`--dry-run`は実行予定の3段階command/pathsを表示するが、fileを書かない。

- core P8
- evidence refresh
- P8/P9 v2

network、通知、runtime、mail、注文を実行しない。

### 10.7 launchd

既存launchdが`tools/run_p8_daily_cycle.py`を呼ぶ構成ならplist変更は不要である。

今回plist、schedule、reloadを変更しない。

---

## 11. 実施パッケージ

### WP9 — 通知association/usefulness再定義

実施内容:

- ambiguous fieldの改名
- notified/unknown/not-notified分離
- human-confirmed分離
- metadata coverage
- operator direction comparison
- latency/PnL descriptive集計
- report JSON/Markdown更新
- causality boundary維持

完了条件:

- 58件を通知有用性58件と表示しない。
- actual associationと通知associationの両方が出る。
- proxy rowがactual usefulnessへ混入しない。

### WP10 — current-generation evidence refresh

実施内容:

- accepted daily output scanner
- deterministic merge
- per-source fingerprint
- v1/v4 cohort分離
- content-addressed history/latest
- source head自動解決
- cutoff自動解決

完了条件:

- current v4 classification cohortが生成される。
- current v4 proxy-trial cohortが生成される。
- 同じ入力で同じrun IDとなる。
- conflictはfail closedする。

### WP11 — formal gate counterfactual report

実施内容:

- shared semantic contract利用
- current vs hard-only counterfactual集計
- other blocker分離
- JSON/Markdown生成

完了条件:

- `execution_gate.py`無変更。
- advisory-only件数と実際にpass可能性が変わる件数を分離できる。

### WP12 — P9品質指標対応

実施内容:

- association coverageとnotification usefulness分離
- quality metrics追加
- claim-specific threshold key追加
- unsupported/invalid/null rate fail closed
- production boundary維持

完了条件:

- 件数だけで品質判定を通過できないclaim scopeを定義可能。
- threshold未指定時に自動eligibleにならない。

### WP13 — daily runner接続

実施内容:

- core成功後のreport-only chain
- previous manifest選択
- partial failure contract
- consolidated status
- dry-run更新

完了条件:

- 既存runnerの1回実行でP8 core、evidence、P8/P9 v2が生成される。
- notification/runtime/order code pathへ接続しない。

### WP14 — acceptanceと正本更新

実施内容:

- code commit後のHEADでacceptance run
- source head自動取得の確認
- current-generation evidence生成
- P8/P9 v2生成
- formal gate impact生成
- CURRENT_STATE更新
- NEXT_ACTION更新

正本更新内容:

```text
評価基盤は日次運用へ接続済み
P9 stateは実生成値
notification usefulnessはdescriptiveで因果未主張
formal gate変更は未承認
次の作業はcounterfactual結果とquality factsの人間レビュー
```

---

## 12. 変更対象ファイル

### 12.1 既存変更候補

```text
src/feedback/manual_trade_modern_attribution.py
src/feedback/p_cumulative_evidence.py
src/feedback/p8_daily_manifest_v2.py
src/feedback/p9_readiness_v2.py
tools/build_p_evidence_bundle.py
tools/build_p8_daily_manifest_v2.py
tools/run_p8_daily_cycle.py
docs/operations/ai-orchestration/CURRENT_STATE.md
docs/operations/ai-orchestration/NEXT_ACTION.md
docs/operations/ai-orchestration/P_SYSTEM_CONTRACT_MAP.md
```

### 12.2 新規候補

```text
src/feedback/formal_gate_semantic_impact.py
tools/refresh_p_current_evidence.py
tests/test_formal_gate_semantic_impact.py
tests/test_refresh_p_current_evidence.py
```

### 12.3 既存test更新候補

```text
tests/test_manual_trade_modern_attribution.py
tests/test_p_cumulative_evidence.py
tests/test_build_p_evidence_bundle_cli.py
tests/test_p8_daily_manifest_v2.py
tests/test_p9_readiness_v2.py
tests/test_build_p8_daily_manifest_v2_cli.py
tests/test_run_p8_daily_cycle.py
```

必要なfileだけを編集する。既存dirty treeをreset、restore、stash、cleanしない。

---

## 13. 出力配置

### 13.1 current evidence

```text
local/reports/p_evidence/p_current_generation/
```

既存acceptance directoryは削除・上書きしない。

### 13.2 daily v2

```text
logs/p8_operating_cycles/YYYYMMDD/p8_v2/
```

既存P8 core filesと同じdirectory直下へ4ファイルを追加せず、subdirectoryで分離する。

### 13.3 output transaction

- historyはrun ID単位でimmutable。
- latestはatomic replacement。
- daily v2は4ファイルをtransactionalに置換。
- failure時に半端なlatestを残さない。
- same identity/different bytesはconflict。

---

## 14. テスト計画

### 14.1 通知有用性

最低限、次をtestする。

1. acceptedだが未通知はnotified countへ入らない。
2. notification status blankはunknownへ入る。
3. low/ambiguous actual linkはacceptedへ入らない。
4. proxy-only rowはactual usefulnessへ入らない。
5. human basis unknownはconfirmedへ入らない。
6. operator side不明はdirection unknown。
7. rate分母0はnull。
8. latency median/p90がdeterministic。
9. automatic causal claimsは常に0。
10. canonical replacementはfalse。

### 14.2 cumulative evidence refresh

1. 複数日を日付順で集約する。
2. v1/v4 cohortを分離する。
3. exact duplicateをdedupeする。
4. identity conflictを停止する。
5. future timestampを停止する。
6. incomplete old directoryはwarningへ記録する。
7. incomplete current directoryは失敗する。
8. per-source fingerprintsを記録する。
9. 同一入力で同一run ID。
10. 新規入力時だけnew historyができる。

### 14.3 formal gate impact

1. advisory-onlyはcounterfactual no-trade blockerから外れる。
2. hard tokenは残る。
3. unknown tokenは残る。
4. mixed hard/advisoryは残る。
5. 他blockerがあればstill blockedへ入る。
6. advisoryだけが唯一blockerの場合のみpotentially changed to pass。
7. production codeをimportしてmutationしない。

### 14.4 P9

1. association coverageとnotification usefulnessが別dimension。
2. notified count 0はcollecting。
3. notified count >0はdescriptive baseline。
4. unsupported requirementは未達。
5. invalid count/rateは未達。
6. null rateはrequirement未達。
7. threshold未freezeはeligibleにならない。
8. v4 cohort欠落時はcollecting。
9. generation mismatchはbaseline reset。
10. production_readyはfalse。

### 14.5 daily runner

1. dry-runは書き込まない。
2. core失敗時は後続を実行しない。
3. evidence失敗時はpartial_failure。
4. P8/P9 v2失敗時はpartial_failure。
5. 全成功時はstatusへrelative pathsを記録。
6. previous manifestは前日以前から選ぶ。
7. 同日既存manifestをpreviousへ使わない。
8. commandにtuning/order/notification routeがない。
9. launchd/plistを変更しない。
10. raw private IDsをstdout/statusへ出さない。

### 14.6 回帰test

今回の新規・関連testに加え、最低限次を実行する。

```text
python -m unittest \
  tests.test_operator_semantics_contract \
  tests.test_generation_identity_contract \
  tests.test_manual_trade_modern_attribution \
  tests.test_p_cumulative_evidence \
  tests.test_build_p_evidence_bundle_cli \
  tests.test_formal_gate_semantic_impact \
  tests.test_refresh_p_current_evidence \
  tests.test_p8_daily_manifest_v2 \
  tests.test_p9_readiness_v2 \
  tests.test_build_p8_daily_manifest_v2_cli \
  tests.test_run_p8_daily_cycle
```

`tools/log_feedback.py`をsubprocess起動する既存testは、repo標準runtime environmentで実行する。AFROG_MCP検証venvの`pandas`欠落を実装回帰として扱わないが、最終報告では環境差を明記する。

---

## 15. Acceptance run

### 15.1 順序

1. implementationとtestsを完了する。
2. source/test変更だけをcommitする。
3. commit後HEADを自動取得してacceptance runする。
4. current evidenceを生成する。
5. current dateのP8/P9 v2を生成する。
6. formal gate semantic impactを生成する。
7. output内容を検証する。
8. canonical docsを更新し、別commitする。

### 15.2 acceptanceで確認する値

最低限、次を報告する。

```text
builder source head
accepted daily directory count
v1 classification rows
v4 classification rows
v1 proxy-trial rows
v4 proxy-trial rows
accepted actual associations
notified accepted actual associations
unknown notification status accepted associations
human-confirmed usefulness count
metadata complete notified actual count
operator direction match/mismatch/unknown
formal advisory-only rows
rows where no-trade blocker would be removed
rows still blocked by other reasons
rows potentially changed to pass
P9 state
P9 missing requirements
```

### 15.3 禁止事項

acceptance runでは次を実行しない。

- real notification
- SMTP
- runtime reload
- launchd reload
- source behavior apply
- formal gate change
- threshold freeze
- proposal approval
- order
- network dependency installation

---

## 16. 完了条件

すべて満たした場合のみ完了とする。

1. 58件が通知有用性として誤表示されない。
2. accepted actual associationとnotified accepted actualが別fieldで出る。
3. human-confirmed usefulnessが別fieldで出る。
4. v4 classification累積cohortが生成される。
5. v4 proxy-trial累積cohortが生成される。
6. daily runnerがcurrent evidenceとP8/P9 v2を自動生成する。
7. source headが自動解決される。
8. cutoffがdeterministicに解決される。
9. formal gate意味差分reportが生成される。
10. `execution_gate.py`が変更されていない。
11. P9が品質requirementを評価できる。
12. threshold未freezeでeligibleにならない。
13. production_readyがfalse。
14. notification/runtime/launchd/mail/orderが不変。
15. 関連testが成功する。
16. acceptance outputがcode commit HEADを記録する。
17. CURRENT_STATEとNEXT_ACTIONが実態へ更新される。
18. unrelated dirty filesをstage/commitしない。

---

## 17. 停止条件

次の場合は推測で進めず停止する。

- 日次classification/trial factsのschemaが日付間で互換でない。
- 同一identityに異なるpayloadが存在する。
- current date outputが不完全。
- timestampがcutoffより未来。
- source HEADを解決できない。
- notification statusの意味を一意に判定できない。
- operator sideを推測しなければdirection比較できない。
- existing production behaviorの変更が必要になる。
- launchd/plist変更が必要になる。
- actual/proxyを分離できない。
- private raw dataをreportへ露出する必要がある。

停止時は、変更済み範囲、原因、必要な人間判断をcompact reportする。

---

## 18. 人間承認境界

### 今回のTASKで許可

```text
report-only source/test changes
current evidence refresh
P8/P9 v2 daily integration
notification usefulness metric correction
formal gate counterfactual report
canonical status documentation
```

### 今回のTASKで不許可

```text
H3 threshold approval
H4 formal gate or Phase1 behavior change
H5 notification trigger change
H6 classifier or production threshold change
H7 runtime/launchd/mail apply
FORMAL_GO
automatic order
canonical actual-link replacement
```

次のproduction gate TASKを作成できるのは、人間が最低限次を確認した後である。

1. advisory-only rowsの件数
2. no-trade blocker除去後も他blockerが残る件数
3. potentially passへ変わる件数
4. actual associationと通知associationの分離結果
5. false positive/false negative review方針
6. rollback/feature flag
7. explicit H4 decision

---

## 19. Commit方針

関連作業は1TASKで実施するが、再現性確保のためcommitを分ける。

### Commit 1

```text
feat: connect P evidence and readiness reporting to daily operation
```

含めるもの:

- source
- tools
- tests
- 本spec

含めないもの:

- generated local reports
- unrelated dirty files
- runtime artifacts

### Acceptance run

Commit 1のHEADをsource headとして自動記録する。

### Commit 2

```text
chore: record P operational evidence acceptance
```

含めるもの:

- CURRENT_STATE
- NEXT_ACTION
- P_SYSTEM_CONTRACT_MAP
- 必要なtracked acceptance summaryのみ

local generated reportsは通常commitしない。既存repo方針でtracked evidenceが必要な場合だけ、最小summaryを追加する。

pushは明示的な既存運用方針に従う。upstreamがない場合やpush許可が不明な場合はcommitまでで停止する。

## FIX2 — 日次rolling snapshotとcurrent evidenceの整合

`manual_operator_classifications.csv`と`manual_operator_trial_facts.csv`はappend-only eventではなく、成功した日次directoryごとのrolling snapshotとして扱う。accepted directoryをYYYYMMDD昇順で処理し、snapshot identityはそれぞれ次の複合キーとする。

- classification: `classification|classifier_method_version|classification_id`
- proxy trial fact: `proxy_trial_fact|classifier_method_version|trial_fact_id`

同一snapshot payloadはexact duplicateとしてdedupeし、同一snapshot identityのmutable payload変更はrevisionとして扱う。selected current date/cutoff以前の最新accepted snapshotを採用し、過去revisionを累積facts/cohortへ二重計上しない。v1/v4はcomponent versionを含むため別cohortとして保持する。immutable anchor（classificationはidentity/source signal/candidate/event timestamp/side/version、trialはidentity/scenario/scenario event/signal/candidate/event timestamp/side/setup/version）が異なる場合だけfail closedし、logical source、identity、first/conflicting date、field名をcompactに返す。canonical episode/link/signal inputsは従来どおりsame identity/different payloadをstrict conflictとする。

refresh manifestは`latest_accepted_snapshot_as_of_cutoff` policy、logical sourceごとのexact duplicate/revised identity/superseded/selected row counts、relative snapshot lineage、selected payload fingerprintを記録する。これらはrun identityへ反映し、同一selected state/source HEAD/cutoffは同一bytes/historyとなる。

formal gate semantic impactのheadline populationはselected latest classification snapshotsのみとし、trial factsはheadlineへ重複加算しない。notification usefulnessのactual categoryはlinked high/mediumかつ`was_notified=true`のactual rowだけに付与し、nonacceptedまたは未通知/unknownはblank、proxy-onlyは別集計とする。`automatic_causal_claims=0`、`causality_status=not_claimed`、`canonical_link_replacement=false`を維持する。

`--current-date`で指定されたYYYYMMDD directoryが不存在、incomplete、unsuccessful、malformed、report-date mismatchの場合は earlier directoryへfallbackせずfail closedする。older historical incomplete directoriesはwarningsとしてのみ保持する。FIX2 acceptanceはselected current date 20260724とcycle manifest由来cutoffを使い、automatic source HEAD resolutionを使用する。同一snapshot identityのmutable revision conflictはinput defectではなくsnapshot collapseで解消し、immutable anchor conflictは停止条件として扱う。
