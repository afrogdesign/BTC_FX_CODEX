---
title: "Phase4自己改善ループ制御計画"
date: 2026-07-07
tags:
  - btc_monitor
  - phase4
  - self-improvement
  - report-only
  - human-decided
---

> [!abstract]
> この文書は、Phase4 の outcome analysis / cue design / display planning / human approval gate を1本の route にまとめる、レポート専用の制御計画です。
> いまの判断は「観測→属性付け→cue設計→表示計画→人間承認待ち」で止め、実装・閾値変更・自動化には進みません。

## 📋 目次

1. [この計画の役割](#この計画の役割)
2. [何が作られてきたか](#何が作られてきたか)
3. [何が変わっていないか](#何が変わっていないか)
4. [現在のブロッカー](#現在のブロッカー)
5. [現在の evidence](#現在のevidence)
6. [現在の cue posture](#現在の-cue-posture)
7. [自己改善ループとの接続](#自己改善ループとの接続)
8. [状態遷移](#状態遷移)
9. [反ドリフト規則](#反ドリフト規則)
10. [次の判断オプション](#次の判断オプション)
11. [Source of Truth](#source-of-truth)

---

## この計画の役割

この計画は、Phase4 の作業が散らばらないようにするための制御文書です。

ここで扱うのは次の流れです。

- AI predictions / notification / reports / dashboard / artifacts を使って、人間が 15m chart を確認する
- その観測から outcome attribution を行う
- resolved-only の what-if / deep dive で cue 候補を分ける
- display/report-label の計画だけを作る
- human approval gate で止める
- 承認された場合のみ、display-only 実装へ進む

これは report-only / human-decided の route です。

---

## 何が作られてきたか

最近の Phase4 では、次のレポート群が整いました。

| 区分 | 作成物 | 役割 |
|---|---|---|
| outcome attribution | `PHASE4_AI_OUTCOME_ATTRIBUTION_PASS2_20260707.md` | prediction と outcome の対応づけ |
| offline what-if | `PHASE4_OFFLINE_WHATIF_SPLIT_REVIEW_20260707.md` | resolved-only の分割候補確認 |
| resolved deep dive | `PHASE4_RESOLVED_CASE_DEEP_DIVE_20260707.md` | V02/V03/V05 の個別深掘り |
| side-aware cue design | `PHASE4_SIDE_AWARE_CUE_DESIGN_20260707.md` | side-aware cue の design candidate 分類 |
| report-label review | `PHASE4_REPORT_LABEL_CUE_DESIGN_REVIEW_20260707.md` | report-label / display-cue の見せ方レビュー |
| no-code implementation plan | `PHASE4_REPORT_LABEL_CUE_IMPLEMENTATION_PLAN_20260707.md` | 将来の表示面だけの導線整理 |

これらは互いに役割が違います。
outcome analysis は事実を分けるため、what-if は候補を比べるため、deep dive は bucket artifact を疑うため、cue design は候補を分類するため、report-label review は operator にどう見せるかを設計するため、implementation plan は将来のファイル/関数候補を並べるためです。

---

## 何が変わっていないか

- display/report-label-only implementation is complete and runtime-applied
- no scoring changes
- no gate changes
- no threshold changes
- no trading logic changes
- no notification trigger changes
- no runtime / launchd changes

このルートは「見せ方をどうするか」を整理するだけで、勝率改善を直接実装するものではありません。

---

## 現在のブロッカー

- Phase4 tuning remains blocked
- human approval required
- report-only / human-decided
- not approved yet

今のルートは `A: stay observation-only` が default です。
人間が明示的に `B` または `C` を選んだときだけ、display/report-label-only の次段階を検討します。

---

## 現在の evidence

### 1. resolved-only の事実

- resolved_intraperiod = `88`
- no_ohlcv = `1742`
- long active_limit_retest は SL-first prone
- short active_limit_retest は TP1-first strong

### 2. deep dive の読み

- V03 long narrow width cue は、V02 q4 position より実体がありそう
- V02 q4 position は artifact risk が高い
- V05 short wide bucket は preserve cue

### 3. latest snapshot の扱い

- Big Chance は review-only / failed thesis の読解用
- Big Chance is not an entry instruction
- Value Defense は shallow zone と defense zone を分けて見る

### 4. self-review の読み

- review_queue_count = 10
- repeated_issue_focus = `entry_filter_or_direction_check`
- human_approval_required = yes
- tuning_review_allowed = no

---

## 現在の cue posture

| Cue | Posture | Interpretation |
|---|---|---|
| CUE01 | design candidate | side-aware review context |
| CUE02 | chart_review_only | long active_limit_retest narrow width cue, not entry prohibition |
| CUE03 | hold / do_not_show_yet | long q4 position, artifact risk |
| CUE04 | preserve cue | short active_limit_retest wide bucket, not removal/tuning cue |
| CUE05 | not_directly_evaluated | stop_distance / ATR, not zero |
| CUE06 | not_directly_evaluated | runner extension, not zero |
| CUE07 | analysis/review quality only | data coverage cue |
| CUE08 | review-only | Big Chance is not an entry instruction |
| CUE09 | review-only | shallow zone と defense zone の分離 |

---

## Runtime application status

- display/report-label-only implementation is complete at commit `d2beafe`
- runtime is already applied
- this does not authorize tuning
- next default state is observation

---

## 自己改善ループとの接続

この route は、既存の self-improvement loop を Phase4 へ接続します。

### Daily proxy loop

- 通知
- 予測
- review queue
- display cue 候補
- proxy outcome

### Weekly review loop

- repeated patterns の drift 点検
- long/short 非対称性の点検
- over-suppression / turning point 見逃しの点検

### Biweekly ground truth loop

- 実取引 import 後に proxy-vs-actual を補正
- 単一例で tuning しない
- actual trade が入って初めて ground truth を確定する

### やらないこと

- no tuning from single examples
- no automatic label promotion
- no entry rule 化
- no runtime change

---

## 状態遷移

```text
Observe
→ Attribute outcome
→ Separate data gap from resolved cases
→ Offline what-if
→ Resolved-case review
→ Cue design
→ Display/report-label plan
→ Human approval gate
→ Display-only implementation if approved
→ Render-only / no-send validation
→ Observation
→ Only later, evidence-backed tuning review
```

この state machine では、`data_gap` と `resolved-only` を混ぜません。
また、`review cue` を `entry rule` にすり替えません。

---

## 反ドリフト規則

- Do not convert review cues into entry rules.
- Do not let "safety" become passivity.
- Do not collapse long/short asymmetry.
- Do not mix no_ohlcv with resolved-only conclusions.
- Do not treat not_directly_evaluated as zero.
- Do not treat Big Chance as entry instruction.
- Do not tune scoring/gates/thresholds without human approval and stronger evidence.

---

## 次の判断オプション

| Option | 意味 | default |
|---|---|---|
| A | stay observation-only | recommended |
| B | approve display/report-label-only implementation | human explicit approval needed |
| C | approve more offline replay/deep-dive only | human explicit approval needed |
| D | wait for actual-trade import / ground truth route | later-stage option |

Recommended current default: **A**

人間が `B` または `C` を明示的に選んだ場合のみ、次の report-label/display-cue 作業に進みます。

---

## Source of Truth

この route は次の順で読むと迷いにくいです。

1. `docs/operations/ai-orchestration/START_HERE.md`
2. `docs/operations/ai-orchestration/PHASE4_SELF_IMPROVEMENT_CONTROL_PLAN_20260707.md`
3. `docs/operations/ai-orchestration/CURRENT_STATE.md`
4. `docs/operations/ai-orchestration/NEXT_ACTION.md`
5. `docs/operations/ai-orchestration/CONTROL.md`
6. `docs/operations/ai-orchestration/PHASE4_*` の個別レポート
7. `docs/operations/strategy/VER04_V1_SELF_IMPROVEMENT_LOOP_FINAL_DESIGN_20260702.md`
8. `docs/operations/strategy/VER04_V1_MANUAL_15M_WIN_DEFINITION_20260702.md`
9. `docs/operations/strategy/VER04_V1_INTEGRATED_PRODUCT_PLAN.md`
