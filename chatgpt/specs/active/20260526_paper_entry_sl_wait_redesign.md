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
> この文書は、Codex に次作業を渡すための確定仕様書です。現状では `trade_execution_gate=pass` と `paper_orders planned` が 0 件のため、実弾化や gate 緩和ではなく、紙ポジションの失敗要因を診断し、entry / wait / SL 条件の改善案を検証可能な形で実装します。

## 📋 目次

- [[#🎯 目的]]
- [[#🌿 対象ブランチ]]
- [[#🧭 現状認識]]
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
3. 実弾 gate は一切緩和せず、まず shadow / paper 診断として安全に観測できる実装にする。

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

## 🧭 現状認識

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

---

## 🧩 変更範囲

### 触ってよいファイル

既存構成に合わせ、必要最小限で変更する。

```txt
tools/log_feedback.py
tests/test_log_feedback.py
運用資料/NEXT_TASK.md
運用資料/履歴/progress.md
reports/analysis/
chatgpt/specs/active/20260526_paper_entry_sl_wait_redesign.md
```

実装上どうしても必要な場合だけ、以下も対象にしてよい。

```txt
src/analysis/
src/trade/
src/notification/
```

ただし、売買判断そのものを即変更するのではなく、まずは診断レポート、shadow flag、paper限定の抑制候補出力に留める。

### 触らないファイル

```txt
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

---

## 🛠 実装内容

### 1. 紙ポジション失敗診断レポートを拡張する

既存の `build-paper-opportunity-diagnostics-report` または同等CLIを確認し、次の集計を追加する。

#### 追加したい切り口

| 切り口 | 見たいこと |
|---|---|
| outcome別 | `tp2_hit` / `sl_hit` / `timeout` / `missed_opportunity` / `entry_not_reached` の差 |
| side別 | `long` と `short` の平均R、PF、勝率、SL率 |
| wait帯別 | `wait<40` / `40<=wait<60` / `60<=wait<80` / `wait>=80` |
| execution帯別 | `execution<20` / `20<=execution<35` / `35<=execution<50` / `execution>=50` |
| market_map flag別 | `support_to_resistance_flip`、`resistance_to_support_flip`、`failed_breakout_*`、`trend_flip_*` |
| entry距離別 | entry到達後にどれくらい逆行してSLへ行ったか |
| MFE/MAE別 | SL候補が一度でもTP1/TP2方向へ伸びていたか |

> [!info]
> 既存CSVに必要カラムがない場合は、現存カラムだけで可能な集計を行い、不足カラムをレポート末尾に `不足データ` として明記する。

---

### 2. `sl_hit` の原因分類を追加する

`sl_hit` を単に失敗として見るのではなく、最低限次の分類へ分ける。

| 分類 | 判定イメージ |
|---|---|
| `early_entry_sl` | entry直後に逆行してSL。entryが早すぎる可能性 |
| `direction_mismatch_sl` | MFEが小さくMAEが大きい。方向判定ミスの可能性 |
| `thin_rr_sl` | RRまたはSL幅が薄く、ノイズで刈られた可能性 |
| `late_wait_sl` | waitが高く、優位性が落ちた状態で入っている可能性 |
| `trend_flip_long_sl` | 上方向転換系 long でSL。現状弱い領域の再確認 |
| `other_sl` | 上記に分類できないもの |

分類は完璧でなくてよい。まずはルールベースでよい。
ただし、各分類の件数、平均R、平均MFE/MAE、代表サンプル timestamp をレポートに出す。

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
| `widen_or_skip_thin_sl` | SL幅が薄い候補はSL拡張ではなくskip優先で検討 |

出力は Markdown レポートにする。
保存先例:

```txt
reports/analysis/paper_entry_sl_wait_redesign_YYYYMMDD.md
```

---

### 4. 安全な shadow flag を追加する

可能なら、実売買や通知ランクには反映せず、ログまたは診断CSVにだけ次の shadow flag を出す。

```txt
paper_shadow_suppress_long_high_wait
paper_shadow_suppress_trend_flip_up
paper_shadow_require_execution_for_high_wait
paper_shadow_delay_sweep_wait_entry
paper_shadow_skip_thin_sl
```

> [!warning]
> この shadow flag は、本番の `trade_execution_gate`、通知ランク、実弾発注可否には絶対に接続しない。まずは観測用にする。

---

### 5. NEXT_TASK と progress を更新する

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
./.venv312/bin/python -m unittest discover -s tests -p "test*.py"
```

該当CLIがある場合は、日付を 2026-05-26 基準で診断レポートを生成する。
実際のコマンド名は既存実装を確認して合わせる。

例:

```bash
./.venv312/bin/python tools/log_feedback.py build-paper-opportunity-diagnostics-report --date 20260526
```

新しいCLI名を追加した場合は、READMEまたは `NEXT_TASK.md` に実行例を書く。

---

## ✅ 完了条件

次の状態になれば完了。

| 条件 | 内容 |
|---|---|
| レポート生成 | `reports/analysis/paper_entry_sl_wait_redesign_YYYYMMDD.md` が生成される |
| SL分類 | `sl_hit` が原因カテゴリ別に集計される |
| 弱い領域の分離 | `long`、`wait>=60`、上方向転換系の成績が分かる |
| proposal出力 | 実装変更ではなく、改善候補として提案が出る |
| 安全性 | 実弾発注、取引所API送信、秘密鍵連携、gate緩和をしていない |
| テスト | `git diff --check` と unittest が通る |
| 記録更新 | `NEXT_TASK.md` と `progress.md` に反映される |

---

## ⚠️ 注意事項

- 今回は `Phase 1B` 昇格作業ではない。
- `Phase 1B-lite` は正式な紙実行候補に混ぜない。
- `trade_execution_gate=pass` を増やすための緩和はしない。
- `trend_flip_confirmed_up` は現状弱いので、強評価へ戻さない。
- `long` と高waitはむしろ抑制候補として扱う。
- SL幅を広げれば見かけ上SLは減るが、損失幅が増えるだけの可能性がある。安易なSL拡張ではなく、skip / delay / confirmation強化を優先する。
- 判断が必要になった場合は、実装せず `確認事項` として報告する。

---

## 📣 Codexへの作業開始指示

```txt
AGENTS.md → chatgpt/README.md → chatgpt/initial_settings.md → chatgpt/specs/active/20260526_paper_entry_sl_wait_redesign.md → 運用資料/NEXT_TASK.md の順に読んでください。

今回の目的は、実弾化や gate 緩和ではありません。
紙ポジションの sl_hit 偏重、long 弱さ、高 wait 弱さ、trend_flip_confirmed_up の弱さを診断し、entry / wait / SL 条件の改善候補をレポート化してください。

実装は診断CLI、Markdownレポート、shadow flag、テスト、NEXT_TASK/progress更新までに留めてください。
trade_execution_gate、通知ランク、実弾発注処理、取引所API送信処理には接続しないでください。
```
