# NEXT TASK TRACKER

## 現在の状況
- Ver01 は本番運用フェーズで、MBP2020 上の `com.afrog.btc-monitor-ver01` を継続監視する段階。
- Ver02 の現時点はタグ `v2.2` として固定予定の内容まで反映済み。
- Ver02 では、Funding を `raw / % / ラベル` で扱う構成に変更し、判定単位を `%` に統一した。
- Ver02 のサポレジは、内部計算用 `all zones` と表示用（近い順 / 強度順）を分離した。
- Ver02 には `signal_tier`（normal / strong_machine / strong_ai_confirmed）と `signal_badge`（🟡/🔥）を実装した。
- 通知トリガーは `signal_tier_upgraded` に対応し、クールダウン中でも段階昇格時は通知できる構成にした。
- 件名と本文にはバッジ表示を追加し、Funding は `ほぼ中立 (+0.0037%)` 形式で出せるようにした。
- CSV/JSON には `funding_rate_raw`、`funding_rate_pct`、`funding_rate_label`、`signal_tier`、`signal_badge` を追加済み。
- 位置フィルター層（`prelabel` / `location_risk` / `risk_flags`）と、Binance 市場構造データの取得は稼働済み。
- 清算イベントは `logs/cache/` へ蓄積する近似実装で運用中。効果検証はこれから。
- 単体テスト（`unittest`）は 7 件追加済みで、現時点は全件成功。
- 打ち合わせノート参照先、ブランチ運用ルール、タグ運用ルール、Obsidian 側の `NEXT_TASK.md` リンク整備は完了済み。
- プロジェクト用 `AGENTS.md` は `btc_monitor/AGENTS.md` へ移動済み。

## 次のタスク
- 1. Ver02 通知を 3〜5 サイクル観察して、`location_risk` / `risk_flags` / `signal_tier` の出方が強すぎないか確認する。
- 2. 強条件（`strong_machine` / `strong_ai_confirmed`）が出た時に、件名バッジ（🟡 / 🔥）と通知理由（`signal_tier_upgraded`）が期待どおり動くか確認する。
- 3. Ver02 の AI要約文を実メールベースで見直し、「方向感」と「いま入る位置」の分離が十分か最終調整する。
- 4. Ver02 の最寄りサポレジ表示（近い順）が実戦感覚とズレる場面を、通知とチャート照合で点検する。
- 5. Ver02 の清算イベント蓄積（`logs/cache`）が実運用で有効かを確認し、必要なら保持秒数・件数を再調整する。
- 6. Ver01 は運用監視として、`logs/last_result.json` と `logs/runtime/monitor.err` の継続更新だけ確認する。

## ブロッカー
- 現時点で明確なブロッカーはなし。
- 強条件（🟡 / 🔥）は市場条件が厳しめに設定されているため、発火確認までに数サイクル必要。

## 完了条件
- Ver01 を安定運用しつつ、Ver02 の Funding表示・近場サポレジ・強条件通知の新仕様を実メールとログ根拠で安定運用できる状態になること。
