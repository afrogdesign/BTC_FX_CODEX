更新日: 2026-03-30 20:10 JST

# Ver02.3 要約層改善: 方向と執行の分離

## まず結論

- 今回は判定ロジック本体の全面改造ではなく、要約層改善が中心です。
- `bias` による方向判断と、「いま執行してよいか」の表示を分離しました。
- `confidence` は引き続き内部キーとして維持しますが、ユーザー向け表示は単独値をやめ、`方向の強さ` `実行しやすさ` `待機圧力` の 3 指標へ分離しました。
- internal reason code や `snake_case` のラベルが本文へ漏れないようにしました。
- `evaluation_trace` を追加し、後で A/B 比較や説明検証をしやすくしました。
- `no_trade_flags` と `risk_flags` の責務も分離し、位置リスクが通知抑止の blocker へ再混入しないようにしました。

## 今回の変更範囲

- `summary` と件名で、必ず `方向判断` と `いまの扱い` を分けて表示するように変更
- `watch` / `invalid` のときは、`ENTRY_OK` でも待機・見送り表現を優先
- `prelabel` の user-facing 表示名を再定義
- `confidence_components` と `confidence_direction_shadow / execution_shadow / wait_shadow` を追加し、本文では 3 指標表示へ切り替え
- `evaluation_trace` を `result` / `last_result.json` / signal snapshot に保存
- `warning_flags` / `risk_flags` / `no_trade_flags` を top-level で責務分離し、`long_setup` / `short_setup` には `blocking_flags` を保持
- `log_feedback` / `log_analytics` に variant と shadow 観測の列を追加

## 補足

- `confidence` はまだ確率ではありません。内部 gate と互換維持のため残しますが、通知本文や件名では主表示にしません。
- 今回は scoring 本体の全面改造はしていません。
- `bias`、`prelabel`、既存の通知判定フロー、CLI/API 切替は維持しています。

## 次段階の候補

- confidence calibration
- paired A/B test
- wait 判断の定量評価
- McNemar 評価
- calibration plot
