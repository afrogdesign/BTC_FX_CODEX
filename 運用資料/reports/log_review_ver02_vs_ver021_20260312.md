# Ver02 と Ver02.1 の通知比較（2026-03-12）

- 補足: これは件名整理前の比較メモです。現在の運用名は `Ver02.1 API` / `Ver02.1 CLI` に統一しています。
- 比較元ログ: `/Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor/logs/last_result.json`, `logs/signals/*.json`, `logs/csv/trades.csv`
- 目的: 件名・本文・AI助言・通知理由コードの差分整理

## Ver02 サマリー
- 件数: 47
- 期間: 20260310_092519.json 〜 20260312_081920.json
- `was_notified=True`: 0 件
- `summary_body` 非空: 47 件
- `ai_decision` 空欄: 14 件
- 件名に「AI審査:機械判定のみ」あり: 2 件
- `reason_for_notification` 内訳: {'agreement_changed': 2, 'confidence_jump': 3, 'prelabel_improved': 2, 'status_upgraded': 1}
- `notify_reason_codes` 内訳: なし
- 先頭件名: [Ver02] [BTC監視] 2026-03-10 18:24 SWEEP_WAIT / long / Confidence 72
- 最新件名: [Ver02] [BTC監視] 2026-03-12 17:19 RISKY_ENTRY / wait / 69,730.30 / Confidence 20

## Ver02.1 サマリー
- 件数: 5
- 期間: 20260312_093528.json 〜 20260312_130500.json
- `was_notified=True`: 0 件
- `summary_body` 非空: 5 件
- `ai_decision` 空欄: 4 件
- 件名に「AI審査:機械判定のみ」あり: 4 件
- `reason_for_notification` 内訳: なし
- `notify_reason_codes` 内訳: なし
- 先頭件名: [Ver02.1] [BTC監視] 2026-03-12 18:35 RISKY_ENTRY / wait / 69,650.20 / Confidence 4
- 最新件名: [Ver02.1] [BTC監視] 2026-03-12 22:05 RISKY_ENTRY / wait / 70,348.50 / Confidence 0 ⚠️ AI審査:機械判定のみ

## 差分の要点
- 件名: Ver02.1 はプレフィックスが `[Ver02.1]` になっており、識別は可能。
- 本文: どちらも本文は入るが、Ver02.1 では AI 応答欠落時に「機械判定のみ」件名が高頻度で付与される。
- AI助言: Ver02 は `ai_decision` が入る回が多い一方、Ver02.1 は 5件中4件で `ai_decision`/`ai_confidence` が空欄。
- 通知理由: 今回比較範囲では `notify_reason_codes` は両版とも 0 件（通知未発生）。
- 通知可否: 両版とも `was_notified=True` は 0 件のため、実メール比較（本文到達比較）は未完了。

## 判断
- 現時点では「件名識別の比較」は完了。
- ただし「実通知メールの比較（件名・本文・AI助言・通知理由コード）」は通知発生待ちで継続。
- `strong_machine` 実検証は実データ待ちとして保留継続。

## 今わかっていること
- この比較では、`Ver02 = API運用`、`Ver02.1 = CLI寄り検証版` として読む前提でよい。
- CLI寄りの Ver02.1 でも `summary_body` 自体は埋まっており、要約生成が全面停止しているわけではない。
- ただし AI助言の安定性は Ver02.1 の方が弱く見える。`ai_decision` 空欄は Ver02 が 47件中14件に対して、Ver02.1 は 5件中4件。
- 件名の `⚠️ AI審査:機械判定のみ` も Ver02.1 で高頻度に出ており、CLI寄り構成では AI 応答欠落時のフォールバックが起きやすい可能性がある。
- 今回の比較範囲では両版とも `was_notified=True` が 0 件なので、「実メール到達後の品質比較」まではまだ進んでいない。

## 未確定なこと
- Ver02.1 の AI 応答欠落が、CLI構成の構造的な弱さなのか、一時的な失敗なのかはまだ断定できない。
- 欠落しているのが AI助言だけなのか、要約側にも不安定さがあるのかは、この資料だけでは十分に切り分けられていない。
- 実通知が出たときに、件名・本文・通知理由コード・到達性にどの程度差が出るかは未確認。
- `strong_machine` や強条件帯で API版と CLI版が同じ判断を返しやすいかも、実データ不足でまだ不明。

## 次に検証すること
1. Ver02.1 側で `ai_decision` が空欄になった回の共通点を洗い、`logs/errors/` と実行時刻を照らす。
2. 要約は成功して助言だけ失敗しているのか、両方とも不安定なのかを切り分ける。
3. 初回の実通知発生時に、Ver02 / Ver02.1 の件名・本文・AI助言・通知理由コードを並べて比較する。
4. 可能なら同じ相場条件帯で数件分ためて、CLI寄り構成でも AI 応答率が安定するかを見る。
5. もし Ver02.1 で欠落が続くなら、CLI 側のタイムアウト、標準出力形式、モデル呼び出し方法のどこがボトルネックかを切り分ける。
