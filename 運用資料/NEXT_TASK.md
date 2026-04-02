# NEXT TASK TRACKER

更新日: 2026-04-02 15:13 JST
運用メモ: このファイルを AI の日常入口にする。実行履歴は `progress.md` に記録し、ここには「次の判断に必要な情報」だけを残す。
補足: フェーズや大型節目の確認が必要になったときだけ [開発ロードマップ.md](開発ロードマップ.md) を開く。
評価シート更新の定型手順: [運用資料/運用/実務/評価シート更新_AI手順.md](運用/実務/評価シート更新_AI手順.md)

## 現在の状況
- 主対象は `iMac 2019` で動かしている `Ver02.3-v5`。日常の通知観測と品質判断はこの 1 本で進める。
- `MBP2020` の `Ver02.1` は `2026-03-31 03:39 JST` に停止し、`/Users/marupro/CODEX/archive/BTC_FX_CODEX_ver02_20260331_0339.tgz` へ凍結退避済み。`mbp2020-btc` は archive 参照用。
- `iMac 2019` の旧 `Ver02.1` 状態同期ジョブ `com.afrog.btc-monitor-status-sync` は停止後に定義ごと整理し、現行運用から外した。旧版参照が必要なときだけ `tools/sync_ver021_prod_status.sh` を手動実行する。
- フェーズはまだ `Ver02.3 / Phase 0 本番観測中`。`Phase 1` へは未昇格。
- ブランチ整理として、`Ver02.3v4` は v5 着手直前の安定点 `7b8c02b` に戻し、AI役割再設計を含む継続作業は `Ver02.3-v5` (`347aea1`) で進める。
- 通知表示は `notification_context` を共通層にして、件名・本文・詳細 HTML・`evaluation_trace` で `ステータス` `執行判断` `方向判断` を同じ順番で出す形へ更新済み。説明メモは [通知共通層_notification_contextメモ.md](運用/実務/通知共通層_notification_contextメモ.md)。
- 詳細 HTML は再検討ラインチャートを主役にした視覚寄りレイアウトへ更新済み。ロング / ショート再検討帯を右の価格軸まで伸ばし、価格軸側で上下限を読む形にした。
- AI の役割は「全サイクル補足」から「通知時監査」へ再設計する方針で整理した。検証と新方針の正本は [AI役割再設計_通知監査移行設計.md](計画/AI役割再設計_通知監査移行設計.md)。
- 通知評価は `HTML + JSON` 正本に切り替え済み。入力正本は `logs/review/review_form_state.json`、集計互換は `logs/csv/user_reviews.csv`、Obsidian 側 `通知評価シート.md` は進捗要約ノート。
- レビュー対象は `2026-03-30 05:05 JST` 以降の通知だけ。古い通知はレビュー画面と集計から外す。
- `2026-03-31 03:24 JST` の `daily-sync` 結果では、完了データ 32 件、全体勝率 71.9%、近似PF 0.75、レビュー要約は `useful_entry=3`、`too_late=1`、平均役立ち度 2.25 / 5。
- `Ver02.3v4` までは、`ENTRY_OK + invalid` の整合補正、`long` 側の反発示唆過大評価の抑制、feedback report の `bias別 direction 正誤` / `risk flag 群別 wrong rate` / `直近12時間速報` を追加済み。
- `Ver02.3-v5` では、AI の役割を「全サイクル補足」から「通知時監査」へ切り替え、通知時だけ `ai_audit` を保存する実装まで完了済み。
- `Ver02.3v4` と `Ver02.3-v5` の差分要約メモを [Ver02.3v4とVer02.3-v5の差分要約.md](計画/Ver02.3v4とVer02.3-v5の差分要約.md) として保存済み。
- 直近確認では `direction_execution_conflict=3件`、`countertrend_long_cluster=4件` を速報で拾える状態になった。
- Global_BOX の `開発環境/iMac 2019` は `2026-04-02 15:28 JST` 時点の実測へ更新済み。現在ロード中は `com.afrog.btc-monitor` のみ。

## 次のタスク
1. AI を通知時のみの監査役に切り替えた後、`main` / `attention` 通知でだけ `ai_audit` が保存され、非通知サイクルでは `skipped_non_notify` になることを確認する。
2. iCloud 側 `評価シート入力フォーム.html` で `2026-03-30 05:05 JST` 以降の通知レビューをためる。保存・再生成だけなら [評価シート更新_AI手順.md](運用/実務/評価シート更新_AI手順.md) を使う。
3. `ENTRY_OK` で `too_late` が再発するかを観測し、`confidence_jump` / `prelabel_improved` / `status_upgraded` の 1 本前で通知できる余地があるかを見る。
4. `NO_TRADE_CANDIDATE` で `skip_too_strict` が再発するかを観測し、再現したら `src/analysis/position_risk.py` の閾値見直し候補として切り出す。
5. `lower_liquidity_close` / `upper_liquidity_close` / `sweep_incomplete` が付いた通知を優先レビューし、risk flag の重みと `notification_context` の主理由表示が納得感と合うかを照合する。
6. レビューがあと 3 件以上たまった段階で `daily-sync` を再実行し、`ロング方向スコアが強すぎる` / `反発示唆の過大評価` / `ENTRY_OK と setup invalid の整合性崩れ` が統計条件に乗るかを再判定する。
7. `NOTIFICATION_HTML_ENABLED=true` で詳細HTMLページ公開とメール末尾 URL 追記が実運用で通るか確認する。あわせて、再検討ラインチャートの視認性と `AI監査メモ` の出現条件が実メール導線でも妥当かを確認する。
8. `Phase 0` 完了条件は「通知後 24 時間評価の一周完了」と「レビュー蓄積」。満たすまでは `Phase 1` へ上げない。

## ブロッカー
- フォームのワンクリック保存には localhost 補助 (`serve-review-form`) の起動が必要。未起動時は localStorage 下書きまで。
- `tests/test_codex_cli_wrapper.py` の不一致は別件として残っているが、通知評価運用より優先度は下げる。
- `tests/test_log_feedback.py` の `test_improvement_candidates_have_expected_limits` は既存レビュー母数依存で現時点 1 件不一致。今回の通知表示改修とは切り分けて扱う。

## 完了条件
- レビュー運用: フォーム保存から `review_form_state.json` / `user_reviews.csv` / Obsidian 要約がそろう状態を維持する。
- Phase 0: 通知発生から 24 時間後評価までを本番で 1 周完了し、レビューを数件ためて傾向を読める状態にする。
- Phase 1: `primary_setup_status=ready` を本有効として、正式指標を実データで確認できる状態にする。現時点では未到達。
