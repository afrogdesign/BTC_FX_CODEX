# NEXT TASK TRACKER

更新日: 2026-04-02 04:35 JST
運用メモ: このファイルを AI の日常入口にする。実行履歴は `progress.md` に記録し、ここには「次の判断に必要な情報」だけを残す。
補足: フェーズや大型節目の確認が必要になったときだけ [開発ロードマップ.md](開発ロードマップ.md) を開く。
評価シート更新の定型手順: [運用資料/運用/実務/評価シート更新_AI手順.md](運用/実務/評価シート更新_AI手順.md)

## 現在の状況
- 主対象は `iMac 2019` で動かしている `Ver02.3v4`。日常の通知観測と品質判断はこの 1 本で進める。
- `MBP2020` の `Ver02.1` は `2026-03-31 03:39 JST` に停止し、`/Users/marupro/CODEX/archive/BTC_FX_CODEX_ver02_20260331_0339.tgz` へ凍結退避済み。`mbp2020-btc` は archive 参照用。
- `iMac 2019` の旧 `Ver02.1` 状態同期ジョブ `com.afrog.btc-monitor-status-sync` は `2026-04-02 04:32 JST` に停止し、plist を `~/Library/LaunchAgents/com.afrog.btc-monitor-status-sync.plist.disabled_20260402_0432` へ退避済み。日常運用から外した。
- フェーズはまだ `Ver02.3 / Phase 0 本番観測中`。`Phase 1` へは未昇格。
- 通知表示は `方向判断` と `いまの扱い` を分離し、本文は `方向の強さ` `実行しやすさ` `待機圧力` の 3 指標表示へ切り替え済み。
- 通知評価は `HTML + JSON` 正本に切り替え済み。入力正本は `logs/review/review_form_state.json`、集計互換は `logs/csv/user_reviews.csv`、Obsidian 側 `通知評価シート.md` は進捗要約ノート。
- レビュー対象は `2026-03-30 05:05 JST` 以降の通知だけ。古い通知はレビュー画面と集計から外す。
- `2026-03-31 03:24 JST` の `daily-sync` 結果では、完了データ 32 件、全体勝率 71.9%、近似PF 0.75、レビュー要約は `useful_entry=3`、`too_late=1`、平均役立ち度 2.25 / 5。
- `Ver02.3v4` では、`ENTRY_OK + invalid` の整合補正、`long` 側の反発示唆過大評価の抑制、feedback report の `bias別 direction 正誤` / `risk flag 群別 wrong rate` / `直近12時間速報` を追加済み。
- 直近確認では `direction_execution_conflict=3件`、`countertrend_long_cluster=4件` を速報で拾える状態になった。
- Global_BOX の `開発環境/iMac 2019` は `2026-04-02 04:33 JST` 時点の実測へ更新済み。現在ロード中として残すのは `com.afrog.btc-monitor` が主、`status-sync` は未ロードへ移した。

## 次のタスク
1. 次回以降の `Ver02.3v4` 通知で、`last_result.json` と実メール件名が `Ver02.3v4` へ切り替わったことを確認する。現時点の保存済み `last_result.json` はまだ `Ver02.3v3-OBS`。
2. iCloud 側 `評価シート入力フォーム.html` で `2026-03-30 05:05 JST` 以降の通知レビューをためる。保存・再生成だけなら [評価シート更新_AI手順.md](運用/実務/評価シート更新_AI手順.md) を使う。
3. `ENTRY_OK` で `too_late` が再発するかを観測し、`confidence_jump` / `prelabel_improved` / `status_upgraded` の 1 本前で通知できる余地があるかを見る。
4. `NO_TRADE_CANDIDATE` で `skip_too_strict` が再発するかを観測し、再現したら `src/analysis/position_risk.py` の閾値見直し候補として切り出す。
5. `lower_liquidity_close` / `upper_liquidity_close` / `sweep_incomplete` が付いた通知を優先レビューし、risk flag の重みと通知文面の納得感を照合する。
6. レビューがあと 3 件以上たまった段階で `daily-sync` を再実行し、`ロング方向スコアが強すぎる` / `反発示唆の過大評価` / `ENTRY_OK と setup invalid の整合性崩れ` が統計条件に乗るかを再判定する。
7. `NOTIFICATION_HTML_ENABLED=true` で詳細HTMLページ公開とメール末尾 URL 追記が実運用で通るか確認する。
8. `Phase 0` 完了条件は「通知後 24 時間評価の一周完了」と「レビュー蓄積」。満たすまでは `Phase 1` へ上げない。

## ブロッカー
- フォームのワンクリック保存には localhost 補助 (`serve-review-form`) の起動が必要。未起動時は localStorage 下書きまで。
- `tests/test_codex_cli_wrapper.py` の不一致は別件として残っているが、通知評価運用より優先度は下げる。

## 完了条件
- レビュー運用: フォーム保存から `review_form_state.json` / `user_reviews.csv` / Obsidian 要約がそろう状態を維持する。
- Phase 0: 通知発生から 24 時間後評価までを本番で 1 周完了し、レビューを数件ためて傾向を読める状態にする。
- Phase 1: `primary_setup_status=ready` を本有効として、正式指標を実データで確認できる状態にする。現時点では未到達。
