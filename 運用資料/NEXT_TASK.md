# NEXT TASK TRACKER

## 現在の状況
- Ver01 は本番運用フェーズで、MBP2020 上の `com.afrog.btc-monitor-ver01` を継続監視する段階。
- Ver02 は開発本線で、`com.afrog.btc-monitor` を再起動済み。今回の表示改善コードは常駐へ反映済み。
- Ver02 では、件名・本文への現在BTC価格表示、サポレジの近接順表示、距離表示、TP順整列まで実装確認済み。
- `last_result.json` では、表示用の `support_zones` / `resistance_zones` は近い順、`support_zones_by_strength` / `resistance_zones_by_strength` は強度順で保持する構成になった。
- 位置フィルター層（`prelabel` / `location_risk` / `risk_flags`）と、Binance 市場構造データの取得は稼働済み。
- 清算イベントは `logs/cache/` へ蓄積する近似実装で運用中。効果検証はこれから。
- 次の見直しは、文面調整なら 2026-03-11、本格的な閾値調整なら Ver02 通知 3〜5 サイクル後が目安。
- 打ち合わせノート参照先、ブランチ運用ルール、タグ運用ルール、Obsidian 側の `NEXT_TASK.md` リンク整備は完了済み。

## 次のタスク
- 1. Ver02 の通知を数サイクル観察して、`location_risk` と `risk_flags` が強すぎるか弱すぎるかを確認する。
- 2. Ver02 の AI要約文を実メールベースで見直し、「方向感」と「いま入る位置」がさらに分かれて読めるよう調整する。
- 3. Ver02 の清算イベント蓄積（`logs/cache`）が実運用で有効かを確認し、必要なら保持秒数・件数を再調整する。
- 4. Ver02 の最寄りサポレジ表示が、実戦感覚とまだズレる場面があるかを通知とチャート照合で確認する。
- 5. Ver01 は運用監視として、`logs/last_result.json` と `logs/runtime/monitor.err` の継続更新だけ確認する。

## ブロッカー
- 現時点で明確なブロッカーはなし。
- 文面調整や閾値調整は、数サイクル分の実通知観察がないと最終判断しにくい。

## 完了条件
- Ver01 を安定運用しつつ、Ver02 の表示改善と位置フィルター調整を実メール・ログ根拠で詰められる状態になること。
