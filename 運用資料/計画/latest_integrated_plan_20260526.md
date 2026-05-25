---
title: "BTC Monitor 最新統合計画"
date: 2026-05-26
tags:
  - BTC_FX_CODEX
  - 自動取引直前
  - PhaseD
  - paper-trading
  - Codex
  - ChatGPT
---

> [!abstract] この文書について
> この文書は、アップロードされた `計画.zip` 内の全計画ファイルを精査し、現在の repo 実装・`NEXT_TASK.md`・最新レポート・active spec と照合したうえで、2026-05-26 時点の最新情報を1枚に統合した計画書です。  
> 古い計画の大半は実装済みまたは置換済みとして扱い、今後取り込む価値がある未実装アイデアだけを Phase D / Phase E の候補として残します。

---

## 📋 目次

- [[#🧭 現在の結論]]
- [[#📌 現在の正本情報]]
- [[#🗂️ 計画ファイル精査結果]]
- [[#✅ 実装済みとして扱うもの]]
- [[#🟡 未実装だが今後取り入れる価値があるもの]]
- [[#🚫 今は取り入れないもの]]
- [[#🔥 現在の最優先実装]]
- [[#🧪 次に見るべき検証数値]]
- [[#🛡️ Phase E で必要になる安全装置]]
- [[#📦 計画ディレクトリ整理方針]]
- [[#✅ 結論]]

---

## 🧭 現在の結論

現在の BTC Monitor は、**紙実行システムの骨格はできているが、まだ自動トレードへ直接進む段階ではない**。

現時点の最重要課題は、実弾 gate を緩めることではなく、`paper_positions.csv` に出ている `sl_hit` 偏重を分解し、負けやすい型を候補化前に弾くことである。

```text
現在地:
Phase C 実装済み・観測中
Phase D 初期段階
Phase E 未到達
```

今やるべきことは、次の active spec の実装である。

```text
chatgpt/specs/active/20260526_entry_wait_trend_flip_quality_guard.md
```

この仕様は「自動トレード実装」ではなく、**自動トレードへ進む前に、紙候補の品質を上げるための仕様**である。

---

## 📌 現在の正本情報

| 項目 | 内容 |
|---|---|
| repo | `afrogdesign/BTC_FX_CODEX` |
| 現在の作業ブランチ | `ver02.6-v2` |
| 運用本体の参照ブランチ | `ver02.5-v8` |
| 現在版 | `Ver02.5-v8` 稼働中 / `ver02.6-v2` で設計・仕様化中 |
| 実務正本 | `運用資料/NEXT_TASK.md` |
| レポート導線 | `運用資料/reports/report_hub_latest.md` |
| ChatGPT 分析 | `chatgpt/analysis/` |
| Codex 実装仕様 | `chatgpt/specs/active/` |
| 現在フェーズ | `Phase C` 実装済み・観測中、`Phase D` 初期 |
| 実弾発注 | 禁止・未実装 |

---

## 🗂️ 計画ファイル精査結果

アップロードされた `計画.zip` 内のファイルを、現在の repo 実装と照合した結果は以下。

| ファイル | 判定 | 理由 |
|---|---|---|
| `README.md` | 現行入口として維持 | 計画フォルダの参照順を示す入口。現在ブランチ・正本導線を明記する用途で必要。 |
| `自動取引直前_高速到達計画_20260518.md` | 統合済み | 基本方針は有効。ただし Phase C 実装済み・Phase D 初期へ進んだため、本書へ統合。 |
| `マイルストーン定義.md` | 参照用に維持 | Phase A-E の定義は有効。Ver02.6 / Ver02.7 / Ver03 / Ver04 の意味を現在地に合わせて読む。 |
| `自動取引直前ロードマップ_やさしい解説_20260522.html` | 履歴扱い | 人間向け説明として有用だが、実務正本にはしない。必要な概念だけ本書へ吸収。 |
| `履歴/評価システム改善仕様書_Ver02x-Ver05接続.md` | 一部採用候補 | `evaluation_trace` の考え方は今後有効。ただし現時点では active spec ではない。 |
| `履歴/改善設計図_v1_チャートパターン拡張.md` | 一部採用候補 | `chart_pattern_shadow` は将来の説明補助として有効。ただし現在の勝ち筋選別より後。 |
| `履歴/AI役割再設計_通知監査移行設計.md` | 実装済み寄り | AI を通知監査・事後評価へ寄せる方針は現在の AI post review 運用に反映済み。 |
| `archive/implemented/*` | 実装済み | 通知ランク、Phase1B-lite、market_map、AI事後評価、Ver02.5-v7 先行実装は現在の実装に反映済み。 |
| `archive/superseded/*` | 置換済み | Phase0-1 / Phase2-3 / 旧マイルストーンは、現在の Phase A-E 設計に置換済み。 |

> [!note]
> `計画/` 直下に複数の「正本っぽいファイル」が残ると、Codex と ChatGPT が迷いやすくなる。  
> 今後は `README.md` とこの最新統合計画を入口にし、日々の実務判断は `NEXT_TASK.md` と `chatgpt/specs/active/` を正本にする。

---

## ✅ 実装済みとして扱うもの

### 1. 通知ランク再設計

実装済み。

- `執行候補・強`
- `執行候補`
- `高優先監視・実行不可`
- `通常監視・実行不可`
- `注意報・売買非推奨`

現在の重要ルールは、**`執行候補` は `trade_execution_gate=pass` かつ `paper_order_status=planned` のときだけ出す**こと。

`opportunity_gate=pass` は実弾候補ではない。

---

### 2. AI 事後評価運用

実装済み。

- `user_reviews.csv`
- AI post review
- `sl_eval`
- `tp_eval`
- `tf_4h_eval / tf_1h_eval / tf_15m_eval`
- `actual_move_driver`
- `logic_validated`
- backlog 管理
- daily cap 管理

現在は AI を毎サイクル自由に走らせるのではなく、**通知後の評価・監査・設計根拠の補助**として使う方向で整理されている。

---

### 3. Phase 1B-lite

実装済み。ただし正式 Phase 1B ではない。

`Phase 1B-lite` は、`SWEEP_WAIT` 限定の専用紙トレード観測レーンとして扱う。

```text
Phase 1B-lite != Phase 1B
Phase 1B-lite != 実弾候補
Phase 1B-lite != paper_orders planned
```

---

### 4. market_map / 下落取り逃し対策

実装済み。

- `support_to_resistance_flip`
- `resistance_to_support_flip`
- `failed_breakout_down_reversal`
- `trend_flip_confirmed_down`
- `trend_flip_confirmed_up`

ただし、現在の分析では、上方向転換系はまだ弱い。

`trend_flip_confirmed_up` は、強評価へ戻さない。

---

### 5. 15分足執行精度チェック

実装済み。

- `execution_precision_action`
- `execution_precision_flags`
- `execution_precision_reason`
- 詳細HTMLの `15分足 執行チェック`

主な目的は、主要ライン直近の追いかけ entry を `wait_only` に落とし、誤った即 entry を減らすこと。

---

### 6. opportunity_gate / paper_positions

実装済み。

- `opportunity_gate`
- `opportunity_type`
- `opportunity_reasons`
- `paper_positions.csv`
- `pending -> opened -> closed`
- `tp2_hit`
- `sl_hit`
- `timeout`
- `missed_opportunity`
- `entry_not_reached`
- `mfe_atr`
- `mae_atr`
- `realized_r`

これにより、実弾なしで「候補が本当に機能したか」を後追いできるようになった。

---

## 🟡 未実装だが今後取り入れる価値があるもの

古い計画群の中で、現在も採用候補として残す価値があるものは以下。

---

### 1. `evaluation_trace` の再導入

旧 `評価システム改善仕様書_Ver02x-Ver05接続.md` にあった構想。

現在は `confidence_direction_shadow`、`confidence_execution_shadow`、`confidence_wait_shadow` などの shadow 指標が増えているため、完全な旧仕様のままではなく、**Phase D 用の説明トレース**として再設計するとよい。

採用候補:

```text
evaluation_trace_version
evaluation_trace.gate_inputs_summary
evaluation_trace.confidence_components
evaluation_trace.entry_quality_components
evaluation_trace.wait_risk_components
evaluation_trace.market_map_components
evaluation_trace.blocker_reason_codes
evaluation_trace.paper_quality_reasons
```

目的:

- なぜ `opportunity_gate=pass` したか
- なぜ quality blocker で止まったか
- なぜ `sl_hit` した可能性が高いか
- どの指標を次に調整すべきか

を、あとから追いやすくする。

> [!warning]
> `evaluation_trace` は、最終判定を変えない内部観測として入れる。  
> score / gate の変更と同じコミットに混ぜない。

---

### 2. quality blocker 別レポート

これは直近で最優先。

`entry / wait / trend_flip` quality guard を入れた後、以下を daily-sync / diagnostics で追う。

```text
paper_quality_high_wait_block
paper_quality_low_execution_block
paper_quality_long_wait_block
paper_quality_trend_flip_up_block
formal_candidate_quality_conflict
```

必要な出力:

- blocker 別件数
- blocker 後の `opportunity_gate=pass` 件数
- blocker 後の `paper_positions` の `sl_hit` 比率
- blocker 後の `missed_opportunity` 増加率
- 有効な market_map 型が削られすぎていないか

---

### 3. `watch_prices` / 次に見る価格

旧 Phase2-3 計画にあった `watch_prices` は、現在も採用価値がある。

ただし、実弾候補を増やすためではなく、**通知の実務価値を上げる補助情報**として使う。

採用候補:

```text
watch_prices.next_support
watch_prices.next_resistance
watch_prices.entry_recheck_zone
watch_prices.invalid_price
watch_prices.recheck_condition
```

用途:

- 「今すぐ入る」ではなく「どの価格まで来たら再検討するか」を明示する
- `missed_opportunity` と `entry_not_reached` の切り分けに使う
- 高 wait 候補を追いかけ entry から再確認待ちへ寄せる

---

### 4. 価格乖離監視

旧 Phase2-3 計画の `価格乖離監視` は、現在の `missed_opportunity` 分析と相性がよい。

採用候補:

```text
distance_to_entry_at_signal_atr
distance_to_tp1_before_entry_atr
distance_to_invalid_atr
entry_zone_reached_after_signal
tp_direction_before_entry
```

用途:

- entry に触れずに TP 方向へ走った候補の分類
- 「早すぎた通知」と「良い候補だが entry が遠かった通知」の分離
- `SWEEP_WAIT` の delayed entry 設計

---

### 5. chart_pattern_shadow

旧 `改善設計図_v1_チャートパターン拡張.md` の構想。

現時点では直接 gate に使わないが、Phase D 後半で、market_map の説明補助として採用価値がある。

採用候補:

```text
chart_pattern_shadow.patterns
chart_pattern_shadow.direction_hint
chart_pattern_shadow.confidence
chart_pattern_shadow.reason_codes
```

候補 pattern:

- `bull_flag`
- `bear_flag`
- `ascending_triangle`
- `descending_triangle`
- `failed_breakout`
- `range_breakdown`
- `range_reclaim`

> [!tip]
> まずは JSON / detail HTML に説明補助として保存するだけにする。  
> score / confidence / gate へ直接反映するのは、型別成績が取れてからにする。

---

### 6. config_change_log

旧計画にあった `config_change_log` は、今後かなり重要。

Phase D では gate や score の調整が増えるため、変更前後の比較ができないと、どの変更が効いたか分からなくなる。

採用候補:

```text
logs/config_change_log.jsonl
logs/csv/config_change_log.csv
```

記録するもの:

- 変更日時
- 変更ファイル
- 変更したパラメータ
- 変更理由
- 参照レポート
- 期待する効果
- rollback 条件

---

### 7. 因子相関分析

旧 Phase2-3 計画の `因子相関分析` は、Phase D の後半で有効。

ただし今すぐではない。

先に quality blocker を入れ、その後に以下を見る。

- `wait`
- `execution`
- `direction`
- `side`
- `market_map_flags`
- `prelabel`
- `exit_status`
- `realized_r`
- `mfe_atr`
- `mae_atr`

目的は、**人間の印象ではなく、どの条件が負けに寄っているかを数字で見ること**。

---

### 8. A/B 比較モード

旧計画の A/B 比較は有効だが、今すぐ大きくやると複雑になる。

採用するなら、まずは shadow 限定。

候補:

```text
baseline_gate_result
candidate_gate_result
baseline_reasons
candidate_reasons
```

用途:

- 現行 opportunity gate
- quality blocker 追加後 gate
- SL/TP 変更前後
- delayed entry 前後

の比較。

---

### 9. Phase E 安全装置

これは未実装で、今後必須。

ただし Phase D の勝ち型選別が終わるまでは実装しない。

必要になるもの:

- kill switch
- blackout window
- 日次損失上限
- 連敗時サイズ縮小
- 最大建玉数
- 同時エントリー数制限
- 取引所API無効状態での dry-run
- 実弾前の最終承認フロー
- manual override
- emergency stop file

---

## 🚫 今は取り入れないもの

| 項目 | 理由 |
|---|---|
| 実弾発注 | `trade_execution_gate=pass` が 0 件で、勝ち型も未確定。 |
| 取引所API送信 | Phase E 未到達。 |
| 秘密鍵連携 | safety layer が未整備。 |
| gate の大幅緩和 | `sl_hit` 偏重が残るため危険。 |
| SL/TP 倍率の先行拡張 | entry / wait / side の失敗が混ざっている。 |
| `trend_flip_confirmed_up` の強評価復帰 | 紙ポジション診断で弱い。 |
| `Phase 1B-lite` の正式昇格 | まだ観測レーン扱い。 |
| AI に通知停止権限を持たせる | まずは監査・評価・説明補助に限定する。 |
| chart pattern を gate に直結 | まだ説明補助の段階。 |
| 大規模 A/B 比較 | quality blocker 後でよい。 |

---

## 🔥 現在の最優先実装

現在の最優先は、以下。

```text
chatgpt/specs/active/20260526_entry_wait_trend_flip_quality_guard.md
```

実装する blocker:

| blocker | 条件 | 目的 |
|---|---|---|
| `paper_quality_high_wait_block` | `confidence_wait_shadow >= 80` | 高 wait で SL に寄る候補を止める。 |
| `paper_quality_low_execution_block` | `confidence_execution_shadow < 20` | 低 execution の弱い entry を止める。 |
| `paper_quality_long_wait_block` | `long_side=true` かつ `wait>=60` かつ `execution<25` | 弱い long + 高 wait を止める。 |
| `paper_quality_trend_flip_up_block` | `long_side=true` かつ `trend_flip_confirmed_up` | 上方向転換系の弱い候補を止める。 |

この実装では `trade_execution_gate` は緩めない。

---

## 🧪 次に見るべき検証数値

quality blocker 実装後に見るべき数値。

| 見るもの | 判断 |
|---|---|
| quality blocker 別件数 | 弱い候補がどの理由で弾かれているか。 |
| blocker 後の `opportunity_gate=pass` | 候補が減りすぎていないか。 |
| blocker 後の `sl_hit` 比率 | 品質ガードが効いているか。 |
| blocker 後の `missed_opportunity` | 弾きすぎて取り逃しが増えていないか。 |
| `support_to_resistance_flip` | 有効な下方向型が残っているか。 |
| `trend_flip_confirmed_up` | 引き続き弱いか。 |
| `long` | long 側を別 gate にすべきか。 |
| `trade_execution_gate=pass` | 自然発生するか。 |
| `paper_orders planned` | 正式紙注文候補が出るか。 |

---

## 🛡️ Phase E で必要になる安全装置

Phase E へ進む条件が整ったら、次を仕様化する。

### 1. kill switch

```text
config/runtime_kill_switch.json
```

または `.kill_switch` ファイルで即停止できるようにする。

### 2. blackout window

重要指標・急変時・低流動時間帯に新規 entry を止める。

### 3. 日次損失上限

```text
daily_loss_limit_r
daily_loss_limit_usd
```

### 4. 連敗時サイズ縮小

既存の `loss_streak_at_entry` と接続する。

### 5. dry-run 実弾直前モード

取引所APIを呼ばずに、注文 payload だけを生成・保存する。

```text
logs/orders/dry_run_orders/*.json
```

### 6. 最終承認フロー

ユーザーが明示許可するまで、取引所への注文送信は実装しない。

---

## 📦 計画ディレクトリ整理方針

今後の `運用資料/計画/` は、次の構造にする。

```text
運用資料/計画/
├── README.md
├── latest_integrated_plan_20260526.md
├── マイルストーン定義.md
├── 履歴/
└── archive/
```

整理ルール:

- `README.md`: 入口。
- `latest_integrated_plan_20260526.md`: 最新統合計画。
- `マイルストーン定義.md`: Phase A-E と Ver 昇格条件の参照用。
- `履歴/`: 過去の設計思想や判断経緯。
- `archive/implemented/`: 実装済み計画。
- `archive/superseded/`: 現行設計に置き換えた旧計画。

---

## ✅ 結論

| 判断項目 | 結論 |
|---|---|
| 現在のフェーズ | `Phase C` 実装済み・観測中、`Phase D` 初期 |
| 自動トレードへ進めるか | まだ早い |
| 今すぐやること | `entry / wait / trend_flip` quality blocker |
| 今やらないこと | 実弾発注、取引所API、秘密鍵、gate 緩和 |
| 古い計画の扱い | ほとんど実装済み・置換済み |
| 今後取り込む価値があるもの | `evaluation_trace`、`watch_prices`、価格乖離監視、`chart_pattern_shadow`、`config_change_log`、因子相関、A/B shadow、Phase E 安全装置 |
| 次の実務正本 | `chatgpt/specs/active/20260526_entry_wait_trend_flip_quality_guard.md` |

最短ルートは、実弾化を急ぐことではない。

**紙候補の負け型を切り分け、勝てる型だけを残し、その後に Phase E の安全装置へ進むこと。**

これが、現時点で最も安全かつ速い自動トレード到達ルートである。
