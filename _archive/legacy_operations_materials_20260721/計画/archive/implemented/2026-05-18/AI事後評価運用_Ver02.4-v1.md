# AI事後評価運用 Ver02.4-v1

更新日: 2026-04-10 10:05 JST

## 1. 何の仕組みか

- この仕組みは、通知メールに書いた予測が後から見て妥当だったかを AI が評価するものです。
- 主に見るのは次です。
  - どの価格なら入るべきだったか
  - ロング / ショートの再検討帯は妥当だったか
  - 損切り価格 `SL` は狭すぎないか / 広すぎないか
  - 利確価格 `TP` は近すぎないか / 遠すぎないか
- 目的は「方向が合っていたか」だけではなく、「実務で使える価格通知だったか」を改善することです。

## 2. 何を材料に評価するか

- 通知時に保存したシグナルJSON
- 24時間後の結果CSV
- 通知時の詳細HTMLから再生成したチャート画像

チャート画像は `4時間足 / 1時間足 / 15分足` の3段です。

- `4時間足`: 大局方向を見る
- `1時間足`: 再検討帯の妥当性を見る
- `15分足`: 実際の入る価格、`SL`、`TP` の精度を見る

一番重要なのは `15分足` です。

## 3. AIが返す評価

AIは `user_reviews.csv` に次のような形で保存されます。

- `user_verdict`
  - `useful_entry`: 入る判断に使えた
  - `useful_wait`: 待つ判断に使えた
  - `useful_skip`: 見送り判断に使えた
  - `too_early`: 早すぎた
  - `too_late`: 遅すぎた
  - `low_value`: 実務価値が低い
- `sl_eval`
  - `good`
  - `too_tight`
  - `too_loose`
- `tp_eval`
  - `good`
  - `too_close`
  - `too_far`
- `tf_4h_eval / tf_1h_eval / tf_15m_eval`
  - `good`
  - `mixed`
  - `poor`

この結果は `daily-sync` のレポートにも集計されます。

## 4. 日常運用のコマンド

### 毎日回すもの

```bash
./.venv312/bin/python tools/log_feedback.py daily-sync
```

- これは日次集計の正本です。
- 既定では `新規AI事後評価を走らせません`。
- 既に保存済みの AI 評価だけを再利用して、`user_reviews.csv`、`shadow_log.csv`、日次レポートを更新します。
- これにより、毎日勝手にクレジットを消費しないようにしています。

### AI評価を少しだけ進めるもの

```bash
./.venv312/bin/python tools/log_feedback.py sync-ai-post-reviews
```

- これは新規の AI 事後評価だけを進める専用コマンドです。
- `daily-sync` とは分けて実行します。

件数を明示したいときは次です。

```bash
./.venv312/bin/python tools/log_feedback.py sync-ai-post-reviews --max-new-ai-reviews 1
```

## 5. クレジット消費を抑える仕組み

Ver02.4-v1 では、AI評価が暴走しないように次の制御を入れています。

- `daily-sync` は既定で新規AI評価をしない
- 既に `review_source=ai` の行は再実行しない
- `logs/review/ai_post_reviews/*.json` があれば再利用する
- 新規AI評価は `sync-ai-post-reviews` でだけ進める
- 1日の新規AI評価上限を設定で管理する
- 既定では `main` 通知だけを優先し、`attention` は後回しにする

現在の既定値は次です。

- `AI_POST_REVIEW_DAILY_MAX=2`
- `AI_POST_REVIEW_PRIORITY_MAIN_ONLY=true`

つまり、通常は `1日最大2件` まで、しかも `main` 通知優先です。

## 6. 優先順位

新規AI評価の候補は次の順で優先されます。

1. `main` 通知
2. `signal_tier` が強いもの
3. 新しい通知

この順で少数件ずつ消化するので、限られたクレジットでも価値の高い通知から評価できます。

## 7. 人のレビューとの関係

- `user_reviews.csv` は AI 正本として使います。
- 人が修正したいときだけ `human_override` にします。
- `human_override` になった行は、以後 AI で上書きしません。

つまり、

- 普段は AI が採点する
- 気になるケースだけ人が直す

という運用です。

## 8. 今の運用判断

現時点では、次の使い分けが基本です。

1. 毎日: `daily-sync`
2. 必要な日だけ: `sync-ai-post-reviews`
3. 一度に多くても `1〜2件`

通知の価格精度を改善したい目的には合っていますが、一括実行するとクレジット消費が大きいため、`少量ずつ進める` 前提で運用します。

## 9. 実運用の自動実行

自動実行は `launchd` で分けています。

- `com.afrog.btc-feedback-daily-sync`
  - 毎日 `03:20 JST`
  - `daily-sync` を実行
- `com.afrog.btc-ai-post-reviews`
  - 毎日 `03:35 JST`
  - `sync-ai-post-reviews` を実行

起動スクリプトは次です。

```bash
zsh tools/start_feedback_jobs.sh
```

この構成にした理由は次です。

- 先に `daily-sync` で日次集計と再利用同期を安定して終わらせる
- その後で少量の新規AI評価を足す
- AI評価が遅くても、日次レポート本体は止めない
