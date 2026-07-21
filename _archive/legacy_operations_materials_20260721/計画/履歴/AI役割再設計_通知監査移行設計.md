# AI役割再設計_通知監査移行設計

更新日: 2026-04-02 14:59 JST

この設計書は、`Ver02.3v4` 時点での AI 利用実態を検証し、今後の役割を「全サイクル補足」から「通知時監査」へ再定義するための正本です。

## 1. 結論

- 現状の AI は、独立した判定エンジンではなく、機械判定の意味づけ・言い換え・補足に留まっている。
- 通知するかどうかは、現状すでに機械判定だけで決まっている。
- このため、AI を全サイクルで回し続ける費用対効果は低い。
- 今後の正しい役割は「通知時だけ走る監査役」とする。
- 当面は AI に通知停止権限を持たせず、まずは誤通知を減らすための監査ログと表示差分だけに使う。

## 2. 現状の実装と役割

### 2.1 実行位置

- [main.py](/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor/main.py) で `request_ai_advice(...)` を呼んでいる。
- 旧実装では `should_notify(...)` より前に無条件実行していたため、実質全サイクルで AI が走っていた。
- 通知可否そのものは [src/notification/trigger.py](/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor/src/notification/trigger.py) の機械条件のみで決まっていた。

### 2.2 AI が返していたもの

- `decision`
- `confidence`
- `primary_reason`
- `warnings`
- `next_condition`

これらは主に本文や詳細 HTML に補足として混ざっていた。

### 2.3 誤解されやすかった点

- `AI_SUMMARY_PROVIDER` という設定名があるが、[src/ai/summary.py](/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor/src/ai/summary.py) の `build_summary_body()` は外部AIを呼ばず、機械データをテンプレート整形しているだけである。
- つまり「本文は AI が自由に考察している」のではなく、「機械判定をコード側テンプレートで文章化している」実装である。

## 3. 検証結果

検証対象:

- [prompts/advice_prompt.md](/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor/prompts/advice_prompt.md)
- [main.py](/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor/main.py)
- [src/notification/trigger.py](/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor/src/notification/trigger.py)
- `logs/signals/*.json`
- `logs/last_result.json`

確認結果:

- `logs/signals` 486件中、`ai_advice` ありは 466件。
- 466件中の AI 判断は次だった。
  - `WAIT_FOR_SWEEP`: 449件
  - 待機系全体: 458件
  - `LONG` / `SHORT`: 7件
- `signal_tier=strong_ai_confirmed` は保存ログ上 0件。
- `ai_next` が通知文の `next_condition_label` にそのまま採用されたのは 32件。
- `ai_reason_present` は 455件あったが、内容の大半は機械理由の言い換えか、`流動性` `RR` `待ち` など既存フラグ由来だった。
- `ai_added_unique_reason` として見えるものは 116件あったが、最近の例では `内部要因のため詳細省略` のような低価値差分も多い。

この結果から、現状の AI は

- 通知可否を決めていない
- signal tier を事実上押し上げてもいない
- 本文や詳細ページでは機械理由の焼き直しになりやすい

という状態であり、費用・遅延・複雑化に対する効果が弱いと判断する。

## 4. 現フェーズでの方針

- 通知可否は機械判定のみを正本として維持する。
- AI は通知時のみ実行する。
- AI の役割は「通知監査」に限定する。
- 最初の評価軸は `見逃し` ではなく `誤通知削減` とする。
- AI は通知を止めない。まずは `agree / caution / disagree` と追加リスクの提示だけ行う。

## 5. 新しい AI の定義

### 5.1 役割名

- `ai_advice` は互換のため残してもよいが、意味としては `ai_audit` を正本にする。

### 5.2 期待する出力

最低限の出力項目は次に固定する。

- `verdict`
  - `appropriate`
  - `borderline`
  - `likely_noise`
- `agreement`
  - `agree`
  - `caution`
  - `disagree`
- `reason`
  - 通知が妥当かどうかの監査理由
- `unique_risks`
  - 機械通知本文に出ていない追加リスク
- `next_review_focus`
  - 人が次にどこを見るべきか
- `audit_variant`

### 5.3 AI にさせないこと

- 方向判定の再計算
- 通知トリガーの直接決定
- 機械スコアの置き換え
- 毎回の長文感想生成

## 6. 実装仕様

### 6.1 実行条件

- `should_notify(...)` の結果 `notify=True` の回だけ AI を実行する。
- `notification_kind=main` と `attention` を対象にする。
- `notify=False` の回は AI を呼ばず、`ai_audit_status=skipped_non_notify` を保存する。

### 6.2 機械判定との関係

- `signal_tier` は機械判定のみで決める。
- `strong_ai_confirmed` は新規生成しない。
- `next_condition_label` は機械由来を正本にする。
- AI の `unique_risks` は、理由主系列には混ぜず別表示にする。

### 6.3 UI / 文面

- 常設の `AI補足の読み解き` は廃止する。
- 差分があるときだけ `AI監査メモ` を表示する。
- 表示条件は次に固定する。
  - `agreement in {caution, disagree}`
  - または `unique_risks` が 1 件以上
- 表示は 3 行以内を原則とする。
  - 監査理由
  - 追加リスク
  - 次の確認観点

## 7. 保存と分析

### 7.1 保存項目

- `ai_audit_status`
- `ai_audit_verdict`
- `ai_audit_agreement`
- `ai_audit_reason`
- `ai_audit_unique_risks`
- `ai_audit_next_review_focus`

### 7.2 レビュー運用で見たい指標

- `likely_noise` だった通知のうち、人レビューで `low_value` / `too_early` / `too_late` に寄る割合
- `agree` だった通知のうち、人レビューで `useful_entry` / `useful_wait` / `useful_skip` に寄る割合
- `caution` / `disagree` が付いた通知で、実際に誤読や不要通知が多いか

## 8. 実装の優先順

1. `request_ai_advice()` を通知時のみ実行へ切り替える
2. `ai_audit` 正本を追加する
3. `signal_tier` から AI 昇格を外す
4. `AI補足` を `AI監査メモ` へ置き換える
5. `csv_logger` と `log_feedback` に監査列を追加する
6. 誤通知レビューとの相関を見られるようにする

## 9. 受け入れ条件

- 非通知サイクルでは AI が呼ばれない
- 通知時だけ AI が呼ばれる
- 通知可否は AI の有無で変わらない
- `signal_tier` が AI 依存で昇格しない
- 通常通知では AI セクションが常に出ない
- `caution` / `disagree` の時だけ `AI監査メモ` が出る
- 監査結果が `logs/signals` と CSV に保存される

## 10. 今回の判断

- 「AI に総合判定させてから通知する」のは理想形としては分かるが、現フェーズではまだ早い。
- まずは機械判定の通知を AI が監査し、誤通知の減少に寄与するかを測る。
- その実測が取れた後にだけ、次段階として「AI に通知停止権限を持たせるか」を再検討する。
