# 評価システム改善仕様書 Ver02.x-Ver05 接続

更新日: 2026-03-18 01:21 JST

この仕様書は、`運用資料/参考資料/BTC判定システム改善案_0317/` を現行 repo 計画へ正式接続するための正本です。
参考資料の発想は活かしますが、実装順と採用範囲は現在の `Ver02.1` / `Phase 0-1` の実情に合わせて固定します。

## 1. まず結論

- 改善案は全面実装せず、段階採用とする。
- 先に採用するのは、`最終判定を変えない内部観測強化` と `仕様の文書化`。
- 先送りするのは、閾値調整、通知件数を増やすための緩和、`build_setup()` の大改修、A/B 比較本格導入。
- 現在の最優先は `Phase 0` の本番確認一周と通知安定化であり、この仕様書はその次段で着手する。

## 2. 現在の前提

- 現在版は `Ver02.1`。
- 現在フェーズは `Phase 0` 実運用確認中で、`Phase 1` は記録基盤まで導入済み。
- `Ver03` は `Phase 0` 完了だけでは名乗らず、`Phase 1` 中核導入と本番記録確認を含めて昇格する。
- 直近の運用課題は、重複メール再発確認、レビュー反映、通知本文の安定化。
- したがって、今すぐ大きく判定ロジックを変える段階ではない。

## 3. 目的

- 今の判定が「なぜそうなったか」を、あとから比較できる形で保存する。
- 将来の `Ver04` / `Ver05` で必要になる分析基盤を、先に安全な形で仕込む。
- 現在の `bias`、`prelabel`、`confidence`、`signal_tier` の意味と実際の通知挙動は、この仕様の初期段階では変えない。

## 4. 非目的

- 通知件数を増やすための閾値緩和
- `sweep` 判定や `setup` 判定そのものの即時改造
- 既存 top-level 出力の意味変更
- AI 自由作文の改善を、この仕様の主目的にすること

補足:

- 通知本文改善は重要だが、別タスクとして扱う。
- この仕様書は「判定を説明しやすくするための内部観測」が主対象。

## 5. 基本方針

- 参考資料の案は、まず `evaluation_trace` として内部ログへ寄せる。
- 既存の top-level 項目は残し、互換性を優先する。
- 追加情報の正本は、まず JSON 系に置く。
- CSV への展開は必要最小限に抑え、列爆発を避ける。
- 1 回の変更で、観測強化と判定ロジック変更を混ぜない。

## 6. 初期実装の対象

初期対象は、`run_cycle()` の途中で既に計算している情報から、比較用の内訳をまとめる部分に限る。

### 6.1 新設する内部項目

- `evaluation_trace_version`
- `evaluation_trace.direction_score_shadow`
- `evaluation_trace.entry_quality_score_shadow`
- `evaluation_trace.trigger_quality_score_shadow`
- `evaluation_trace.trigger_reason_codes`
- `evaluation_trace.risk_component_scores`
- `evaluation_trace.confidence_components`
- `evaluation_trace.setup_decision_reason_codes`
- `evaluation_trace.signal_tier_inputs_summary`

### 6.2 初期保存先

- `result`
- `logs/last_result.json`
- `logs/signals/*.json`
- snapshot JSON

### 6.3 この段階で維持する既存出力

- `bias`
- `prelabel`
- `confidence`
- `signal_tier`
- `notify_reason_codes`
- `suppress_reason_codes`

補足:

- この段階では、上記の最終結果が変わらないことを最重要にする。

## 7. 追加項目の意味

### `direction_score_shadow`

- 現行の `compute_scores()` に近い方向感の補助点を、比較用にまとめた値。
- top-level の `long_display_score` / `short_display_score` を置き換えず、説明補助として扱う。

### `entry_quality_score_shadow`

- 現在位置で仕掛ける質を、`RR`、距離、support / resistance、warning などからまとめた比較用スコア。
- 既存の `build_setup()` や `evaluate_position_risk()` の決定を置き換えない。

### `trigger_quality_score_shadow`

- 「今すぐ入る質」があるかを、trigger readiness、zone 到達、warning cluster などから比較用にまとめる値。

### `trigger_reason_codes`

- trigger 成立、不成立、見送り理由をコード化した一覧。

### `risk_component_scores`

- `evaluate_position_risk()` の内訳を、比較しやすい形で保存する辞書。

### `confidence_components`

- `compute_confidence()` が加点・減点した理由を、比較用に分解して保存する辞書または配列。

### `setup_decision_reason_codes`

- `build_setup()` と primary setup の選択理由を、比較用コードとして保存する。

### `signal_tier_inputs_summary`

- `compute_signal_tier()` が見た主要条件を、あとから追える最小要約。

## 8. 実装順

### Step A ドキュメント固定

- この仕様書を正本として追加する。
- `NEXT_TASK.md` と `開発ロードマップ.md` に「改善案は段階採用」と明記する。

### Step B 着手条件の達成

- `通知評価シート.md` で `review_status=done` を 1 件以上作る。
- 重複メール再発が止まっていることを確認する。
- 通知本文改善を別タスクとして切り分ける。

### Step C `evaluation_trace` の最小実装

- 既存判定を変えずに、内部比較項目だけ追加する。
- 正本は JSON に保存する。

### Step D 比較検証

- 同一入力で `bias`、`prelabel`、`confidence`、`signal_tier` が不変であることを確認する。
- 将来の `Ver04` / `Ver05` で流用できる比較材料になっているか確認する。

## 9. テスト方針

- 同一入力で最終判定が変わらないことを確認する。
- `last_result.json` と signal snapshot に `evaluation_trace` が自然に保存されることを確認する。
- 既存の `daily-sync`、CSV 保存、通知判定を壊さないことを確認する。
- 判定変更と観測追加を同じコミットに混ぜない。

## 10. リスク

- 先に shadow 指標を広げすぎると、今の `Phase 0` 運用確認と焦点がぶれる。
- CSV に列を増やしすぎると、レビュー運用が重くなる。
- 既存 top-level と shadow 指標の意味が混ざると、後で判断軸が二重化する。

## 11. 完了条件

### この仕様書の段階完了

- 正式計画へ採用判断が反映されている。
- 次に実装する shadow 項目が固定されている。
- 「今やらないこと」が文書で固定されている。

### コード着手完了

- `evaluation_trace` 最小版が JSON に保存される。
- 既存の最終判定と通知挙動が変わらないことを確認できる。

## 12. 将来フェーズとの接続

- `Ver02.x` では、比較可能な内部観測として使う。
- `Ver03` では、`Phase 0` / `Phase 1` の本番結果と照らして説明補助に使う。
- `Ver04` では、構造化 AI 審査や通知品質改善の比較土台に使う。
- `Ver05` では、prelabel 内部スコア化や A/B 比較モードの入力基盤として使う。
