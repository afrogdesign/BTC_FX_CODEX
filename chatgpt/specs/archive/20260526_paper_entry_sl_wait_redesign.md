---
title: 紙ポジションのSL偏重と高wait弱さを診断し、entry条件を再設計する
date: 2026-05-26
tags:
  - btc-monitor
  - spec
  - codex
  - paper-trade
  - entry-redesign
---

> [!abstract]
> この文書は、Codex に次作業を渡すための確定仕様書です。repo 精査の結果、既存の `tools/log_feedback.py` には `build-paper-opportunity-diagnostics-report` が実在し、`paper_positions.csv`、`shadow_log.csv`、`market_map_flags`、`confidence_*_shadow` を結合した診断基盤もあります。したがって今回は、売買ロジック本体を触らず、既存診断レポートの拡張に絞ります。

## 📋 目次

- [[#🎯 目的]]
- [[#🌿 対象ブランチ]]
- [[#🧭 repo精査後の現状認識]]
- [[#🧩 変更範囲]]
- [[#🛠 実装内容]]
- [[#🧪 検証方法]]
- [[#✅ 完了条件]]
- [[#⚠️ 注意事項]]
- [[#📣 Codexへの作業開始指示]]

---

## 🎯 目的

紙ポジションの直近成績では、`missed_opportunity` より `sl_hit` が主失敗になっている。
また、`market_map_opportunity` は累計では改善傾向がある一方で、`long`、`wait>=60`、`resistance_to_support_flip`、`trend_flip_confirmed_up` が弱い。

この仕様の目的は次の 3 点。

1. `sl_hit` 偏重が、entryの早すぎ、SL幅の狭すぎ、方向判定の弱さ、または高wait候補の混入によるものかを切り分ける。
2. `long` / `wait>=60` / 上方向転換系を、紙候補から抑制すべきか、entry条件を遅らせるべきか、SL/TP設計を変えるべきか判断できるレポートを作る。
3. 実弾 gate は一切緩和せず、既存診断CLIの拡張として安全に観測できる形にする。

---

## 🌿 対象ブランチ

```txt
ver02.6-v1
```

作業前に必ず次を実行する。

```bash
git checkout ver02.6-v1
git pull origin ver02.6-v1
```

---

## 🧭 repo精査後の現状認識

`運用資料/NEXT_TASK.md` の 2026-05-26 JST 時点を正本とする。

重要な前提は次の通り。

| 項目 | 状態 |
|---|---|
| 運用本体 | `ver02.5-v8` |
| 作業ブランチ | `ver02.6-v1` |
| `trade_execution_gate=pass` | 0 件 |
| `paper_orders planned` | 0 件 |
| `Phase 1B-lite` | 5 件で観測中。正式 Phase 1B ではない |
| 直近の主失敗 | `sl_hit=12件`、`missed_opportunity=5件` |
| 弱い領域 | `long`、`wait>=60`、`trend_flip_confirmed_up`、上方向転換系 |
| 禁止事項 | 実弾発注、取引所API送信、秘密鍵連携、gate緩和 |

repo上で確認済みの事実。

| 確認対象 | 確認内容 |
|---|---|
| `tools/log_feedback.py` | `build_paper_opportunity_diagnostics_report()` が実在する |
| CLI | `build-paper-opportunity-diagnostics-report` が argparse に登録済み |
| 既存テスト | `tests/test_log_feedback.py` に `test_paper_opportunity_diagnostics_report_groups_market_map_failures` が存在する |
| `PAPER_POSITION_HEADER` | `side`、`exit_status`、`mfe_atr`、`mae_atr`、`realized_r`、`confidence_*_shadow`、`market_map_flags` を保持している |
| 既存レポート | confidence帯別、setup reason別、side別、market_map flag別、opportunity reason別、弱い代表例は既に出せる |

> [!warning]
> したがって、今回 Codex がやるべきことは「新しい売買判定を実装すること」ではなく、「既存診断レポートの不足部分を増やすこと」です。

---

## 🧩 変更範囲

### 原則として触ってよいファイル

```txt
tools/log_feedback.py
tests/test_log_feedback.py
運用資料/NEXT_TASK.md
運用資料/履歴/progress.md
chatgpt/specs/active/20260526_paper_entry_sl_wait_redesign.md
```

### 生成してよいレポート

既存の `運用資料/reports/analysis/` 配下に合わせる。

```txt
運用資料/reports/analysis/paper_entry_sl_wait_redesign_YYYYMMDD.md
```

既存の実行例に合わせ、必要なら `--output-md` で明示する。

```bash
./.venv312/bin/python tools/log_feedback.py build-paper-opportunity-diagnostics-report \
  --date-from 2026-04-18 \
  --date-to 2026-05-26 \
  --output-md 運用資料/reports/analysis/paper_entry_sl_wait_redesign_20260526.md
```

### 今回は触らないファイル

```txt
src/analysis/
src/trade/
src/notification/
config.py
.env
.env.*
secrets/
logs/runtime/*.err
logs/heartbeat.txt
logs/last_result.json
paper_positions.csv の既存履歴を破壊する変更
取引所API送信処理
実弾発注処理
```

> [!danger]
> 前版の仕様書では `src/analysis/`、`src/trade/`、`src/notification/` を「必要なら触ってよい」としていたが、repo精査後は撤回する。今回の実装は `tools/log_feedback.py` とテストに閉じる。

---

## 🛠 実装内容

### 1. 既存診断レポートを拡張する

既存の `build_paper_opportunity_diagnostics_report()` を拡張する。
新しいCLIを増やす必要は原則ない。

既にある集計は壊さず、下記を追加する。

#### 追加する切り口

| 切り口 | 見たいこと |
|---|---|
| exit_status別 | `tp2_hit` / `sl_hit` / `timeout` / `missed_opportunity` / `entry_not_reached` の差 |
| side別 | `long` と `short` の平均R、PF、勝率、SL率 |
| wait帯別 | `wait<40` / `40<=wait<60` / `60<=wait<80` / `wait>=80` |
| execution帯別 | `execution<20` / `20<=execution<35` / `35<=execution<50` / `execution>=50` |
| market_map flag別 | `support_to_resistance_flip`、`resistance_to_support_flip`、`failed_breakout_*`、`trend_flip_*` |
| SL原因分類別 | `early_entry_sl` 等の原因分類 |
| MFE/MAE別 | SL候補が一度でもTP方向へ伸びていたか |

> [!info]
> 既存CSVに必要カラムがない場合は、現存カラムだけで可能な集計を行い、不足カラムをレポート末尾に `不足データ` として明記する。

---

### 2. `sl_hit` の原因分類をレポート内に追加する

`sl_hit` を単に失敗として見るのではなく、最低限次の分類へ分ける。

| 分類 | 判定イメージ |
|---|---|
| `early_entry_sl` | entry後に十分なMFEが出る前にMAEが大きい。entryが早すぎる可能性 |
| `direction_mismatch_sl` | MFEが小さくMAEが大きい。方向判定ミスの可能性 |
| `thin_rr_sl` | RRまたはSL幅が薄く、ノイズで刈られた可能性 |
| `late_wait_sl` | `confidence_wait_shadow>=60`。優位性が落ちた状態で入っている可能性 |
| `trend_flip_long_sl` | `side=long` かつ `trend_flip_confirmed_up` を含むSL |
| `other_sl` | 上記に分類できないもの |

実装は `tools/log_feedback.py` 内のヘルパー関数でよい。
例:

```txt
_classify_sl_failure(row) -> str
_sl_failure_group_lines(rows) -> list[str]
```

分類は完璧でなくてよい。
ただし、各分類について最低限次を出す。

- 件数
- 平均R
- 簡易PF
- 平均 `mfe_atr`
- 平均 `mae_atr`
- 代表 `signal_id`

---

### 3. 改善候補を `proposal` として出す

Codex は勝手に本番 gate を変えない。
代わりに、診断レポート内で次のような改善候補を `proposal` として出す。

| proposal | 内容 |
|---|---|
| `suppress_long_high_wait` | `long` かつ `wait>=60` は紙候補から一段抑制候補 |
| `suppress_trend_flip_up_strong` | `trend_flip_confirmed_up` を強評価へ戻さない |
| `require_execution_for_high_wait` | `wait>=60` の場合は execution 下限を上げる候補 |
| `delay_entry_on_sweep_wait` | `SWEEP_WAIT` 系は即entryではなく再確認待ちへ寄せる候補 |
| `skip_thin_sl` | SL幅が薄い候補はSL拡張ではなくskip優先で検討 |

この `proposal` はレポート文言だけにする。
`trade_execution_gate`、`opportunity_gate`、`paper_order_status`、通知ランクには反映しない。

---

### 4. shadow flag はCSVスキーマに追加しない

前版の仕様書では `paper_shadow_*` のような shadow flag を追加すると読める箇所があったが、repo精査後は撤回する。

今回追加してよいのは、Markdownレポート内の診断ラベルだけ。

```txt
paper_shadow_suppress_long_high_wait
paper_shadow_suppress_trend_flip_up
paper_shadow_require_execution_for_high_wait
paper_shadow_delay_sweep_wait_entry
paper_shadow_skip_thin_sl
```

上記の文字列を使う場合も、CSVカラム追加ではなく `proposal` または `診断ラベル` としてレポートに出すだけにする。

> [!danger]
> `CSV_HEADER`、`SHADOW_HEADER`、`PAPER_POSITION_HEADER` のスキーマ変更は禁止。既存ログ互換性を壊さない。

---

### 5. 既存テストを壊さず、追加テストを書く

既存の `tests/test_log_feedback.py` には、紙ポジション診断のテストがある。
これを壊さず、最低1つ追加する。

追加テストの方向。

```txt
test_paper_opportunity_diagnostics_report_classifies_sl_failures
```

確認したい内容。

- `sl_hit` 行が `late_wait_sl` などに分類される
- `long` / `wait>=60` / `trend_flip_confirmed_up` の proposal がレポートに出る
- 既存文言 `紙実行候補 entry/wait 診断` が維持される

---

### 6. NEXT_TASK と progress を更新する

作業後、以下を更新する。

```txt
運用資料/NEXT_TASK.md
運用資料/履歴/progress.md
```

最低限、次を記録する。

- 追加したレポート名
- 実行したコマンド
- テスト結果
- 主要な診断結果
- gate緩和を行っていないこと
- 次に ChatGPT 側で判断すべき論点

---

## 🧪 検証方法

最低限、次を実行する。

```bash
git diff --check
./.venv312/bin/python -m unittest tests.test_log_feedback
./.venv312/bin/python -m unittest discover -s tests -p "test*.py"
```

診断レポート生成は、既存CLIを使う。
`--date` は存在しないため使わない。

```bash
./.venv312/bin/python tools/log_feedback.py build-paper-opportunity-diagnostics-report \
  --date-from 2026-04-18 \
  --date-to 2026-05-26 \
  --output-md 運用資料/reports/analysis/paper_entry_sl_wait_redesign_20260526.md
```

---

## ✅ 完了条件

次の状態になれば完了。

| 条件 | 内容 |
|---|---|
| レポート生成 | `運用資料/reports/analysis/paper_entry_sl_wait_redesign_20260526.md` が生成される |
| SL分類 | `sl_hit` が原因カテゴリ別に集計される |
| 弱い領域の分離 | `long`、`wait>=60`、上方向転換系の成績が分かる |
| proposal出力 | 実装変更ではなく、改善候補として提案が出る |
| スキーマ維持 | `CSV_HEADER`、`SHADOW_HEADER`、`PAPER_POSITION_HEADER` を変更していない |
| 安全性 | 実弾発注、取引所API送信、秘密鍵連携、gate緩和をしていない |
| テスト | `git diff --check`、`tests.test_log_feedback`、全体 unittest が通る |
| 記録更新 | `NEXT_TASK.md` と `progress.md` に反映される |

---

## ⚠️ 注意事項

- 今回は `Phase 1B` 昇格作業ではない。
- `Phase 1B-lite` は正式な紙実行候補に混ぜない。
- `trade_execution_gate=pass` を増やすための緩和はしない。
- `opportunity_gate` の条件も変更しない。
- `trend_flip_confirmed_up` は現状弱いので、強評価へ戻さない。
- `long` と高waitはむしろ抑制候補として扱う。
- SL幅を広げれば見かけ上SLは減るが、損失幅が増えるだけの可能性がある。安易なSL拡張ではなく、skip / delay / confirmation強化を優先する。
- 判断が必要になった場合は、実装せず `確認事項` として報告する。

---

## 📣 Codexへの作業開始指示

```txt
AGENTS.md → chatgpt/README.md → chatgpt/initial_settings.md → chatgpt/specs/active/20260526_paper_entry_sl_wait_redesign.md → 運用資料/NEXT_TASK.md の順に読んでください。

今回の目的は、実弾化や gate 緩和ではありません。
既存の tools/log_feedback.py にある build_paper_opportunity_diagnostics_report() を拡張し、紙ポジションの sl_hit 偏重、long 弱さ、高 wait 弱さ、trend_flip_confirmed_up の弱さを診断してください。

実装は tools/log_feedback.py、tests/test_log_feedback.py、Markdownレポート、NEXT_TASK/progress更新までに留めてください。
src/analysis、src/trade、src/notification、CSVスキーマ、trade_execution_gate、opportunity_gate、通知ランク、実弾発注処理、取引所API送信処理には接続しないでください。
```
