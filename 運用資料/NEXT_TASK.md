# NEXT TASK TRACKER

更新日: 2026-03-19 02:33 JST
運用メモ: このファイルを AI の日常入口にする。実行履歴は `progress.md` に記録し、ここには「次の判断に必要な情報」だけを残す。
補足: フェーズや大型節目の確認が必要になったときだけ [開発ロードマップ.md](開発ロードマップ.md) を開く。

## 現在の状況
- 現在の役割は固定済み。本番は `Ver02.1 API` を 1 本だけ稼働、開発 `Ver02.1 CLI` 常駐は `2026-03-17 04:48 JST` に停止して切り分け観測へ入った。`Ver01` 本番常駐は `2026-03-16 19:14 JST` に停止済み、旧 `Ver02.1 API` 実体は `/Users/marupro/CODEX/BTC_FX_CODEX_ver02_API_backup_20260316_2030` へ退避済み。
- 日常の本番確認は `zsh tools/sync_ver021_prod_status.sh` で軽量同期し、まず `tmp/status/prod_status_summary.md` と `tmp/status/prod_status_sync_last_success.txt` だけを見る。
- 本番軽量同期ジョブ `com.afrog.btc-monitor-status-sync` は常設運用とし、一時ジョブ扱いにしない。
- 開発環境で「何が動いているか」は `運用資料/運用/環境/開発環境_実行ファイル一覧.md` と `/Users/marupro/CODEX/Global_BOX/10_共通仕様/開発環境_実行ファイル一覧.md` を入口に確認する。
- 詳細取得は鍵認証の `tools/pull_ver021_prod_logs_auto.sh` を標準とし、パスワード版は例外手順に分離済み。
- `Phase 1` の土台実装は完了しており、今は通知発生待ちで実データ評価にはまだ入っていない。
- 上昇初動の取り逃がし対策として、実効設定を `CONFIDENCE_LONG_MIN=40`、`MIN_RR_RATIO=1.15`、`sweep_incomplete=+4` へ調整済み。確認入口は `運用資料/運用/調整/採点調整シート.md`。
- 本命通知とは別に `注意報メール` を追加済み。件名の強さレイヤーは `👀 [注意報]`、`🟡 好条件接近`、`🔥 ゴールデン条件`。
- 注意報の閾値は `ATTENTION_ALERT_SCORE_MIN=52`、`ATTENTION_ALERT_GAP_MIN=12`、`ATTENTION_ALERT_COOLDOWN_MINUTES=30`。本命通知とは別履歴で管理する。
- `Ver01` は比較完了として常駐停止済み。以後の観測と改善判断は `Ver02.1` を主対象に進める。
- 本番 `Ver02.1 API` は 2026-03-19 02:33 JST に `.env` の `AI_ADVICE_PROVIDER` / `AI_SUMMARY_PROVIDER` を `api` へ戻し、`com.afrog.btc-monitor-ver021` を再起動した。再起動後は `state = running`、`pid = 39245`、設定読込も `api / api` を確認済み。
- 通知メールの本文と件名は 2026-03-17 05:17 JST 時点で改善版を本番へ反映済み。本文は待機回でも再検討帯 / 損切り / TP1 / TP2 を残し、件名は `【BTC:価格】` と `信頼度xx` を含む日本語中心の形へ変更した。
- 2026-03-17 05:05 JST の実メール確認で、AI自由作文は改行・用語・見出し品質のブレがまだ大きいと判断した。次回改善は「AI作文なし、コード側テンプレート主導」を優先課題にする。
- 現行の `sweep` 判定は、直近高安への接近を使った近似ロジックであり、「本当に狩って戻したか」までは見ていない。`sweep_incomplete` の精度には改善余地がある前提で扱う。
- `運用資料/参考資料/BTC判定システム改善案_0317/` の採用判断を整理し、全面実装ではなく段階採用とした。正式方針は `運用資料/計画/評価システム改善仕様書_Ver02x-Ver05接続.md` を正本にし、直近は最終判定を変えない内部観測強化だけを次段候補として扱う。
- この実行環境では外部 SSH が制限されることがあり、失敗時は疎通可能環境で再試行する。

## 次のタスク
1. しばらくは `tmp/status/prod_status_summary.md` を入口に、本番 `Ver02.1 API` 1本運用での自然更新と通知品質を観測し、同件名の重複メールが再発しないかを優先確認する。
2. 次回通知または異常が出たときだけ `zsh tools/pull_ver021_prod_logs_auto.sh` で詳細を掘り、本番側で `ai_advice_error` / `ai_summary_error` が出ていないか、改善後の件名と本文が意図どおり見えるかを確認する。
3. 次回の通知改善では、AI自由作文を外し、コード側テンプレート主導で本文を固定化する方向の設計を優先して検討する。あわせて `signal_id` 単位の重複送信防止ガードも候補に含める。
4. `sweep_incomplete` は現在近似判定なので、次回の判定改善では「高安へ近づいた」だけでなく「狩って戻したか」まで見られるかを検討する。
5. 本命通知されないロング回や違和感のある本文・件名が出たときだけ、`運用資料/運用/調整/採点調整シート.md` と `運用資料/参考資料/自然文章化設計書.md` を入口に見直す。
6. `通知評価シート.md` で `review_status=done` を1件以上作り、`logic_validated` と `Phase 1` の正式評価開始へつなげる。
7. 重複メール再発が止まっていることと、通知本文の template 主導化方針を切り分けたうえで、`評価システム改善仕様書_Ver02x-Ver05接続.md` に沿った `evaluation_trace` 最小版の実装順を固める。
8. `evaluation_trace` に入れる項目は、`direction_score_shadow`、`entry_quality_score_shadow`、`trigger_quality_score_shadow`、`trigger_reason_codes`、`risk_component_scores`、`confidence_components`、`setup_decision_reason_codes`、`signal_tier_inputs_summary` を初期候補とし、既存の `bias` / `prelabel` / `confidence` / `signal_tier` は変えない前提で進める。

## ブロッカー
- 直近の急ぎブロッカーはない。現在は本番観測フェーズ。
- `daily-sync` は 2026-03-18 00:33 JST に初回実行済み。`signal_outcomes.csv` と `user_reviews.csv` は生成されたが、`user_reviews.csv` はまだヘッダーのみで、レビュー反映が未実施のため `logic_validated` の本番評価にはまだ進み切れていない。
- `phase1_active` は実装済みだが、本番 `API` へ戻した直後のため、直近の自然更新母数はまだ少ない。
- `BTC判定システム改善案_0317` のうち shadow 指標追加は有望だが、着手前に `Phase 0` のレビュー反映と通知安定確認を先に満たす必要がある。

## 完了条件
- Phase 0: 通知発生から 24 時間後評価まで（`daily-sync` + レビュー反映）を本番で 1 周完了。
- Phase 1: `primary_setup_status=ready` を本有効として、正式指標を実データで確認できる状態にする。
