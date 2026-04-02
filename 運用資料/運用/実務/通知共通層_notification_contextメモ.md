# 通知共通層 `notification_context` メモ

更新日: 2026-04-02 14:35 JST

このメモは、`Ver02.3v4` で追加した通知共通層 `notification_context` の役割を短く確認するための実務メモです。

## まず結論

- 通知の見え方を、`方向通知` ではなく `行動判断通知` としてそろえるための派生表示層です。
- 判定ロジック本体は維持し、`bias` `prelabel` `primary_setup_status` `notification_kind` `flags` から通知用の意味をまとめて作ります。
- 件名、本文、詳細 HTML、`evaluation_trace` が同じ判断ラベルを使うようにしました。

## 何が入るか

- `status_code`
  - `attention` `monitor` `actionable` `invalid` `neutral`
- `status_label`
  - `注意報` `監視` `執行可` `無効` `中立`
- `status_explanation`
  - 方向変化の早期共有 / 条件接近 / 条件成立 / 執行不可
- `execution_label`
  - `見送り` `監視継続` `条件付きで検討`
- `entry_window_label`
  - 現値帯のみ条件付き / 近接帯のみ条件付き / 発火条件待ち / 価格到達待ち / 不可
- `reason_labels`
  - 通知で最初に見せる主理由 3 件
- `reason_labels_full`
  - 詳細表示用の理由一覧
- `next_condition_label`
  - 次に何を見たら再評価するか
- `invalidation_label`
  - どこを崩したら無効寄りか
- `validity_label`
  - いつまで有効目安とみなすか
- `rr_summary_label`
  - `想定RR 1.19（基準付近）` のような短文
- `price_map`
  - 近いサポート / レジスタンス

## 読み方

- 先に `ステータス` と `執行判断` を見る
- 次に `方向判断` を見る
- そのあと `主理由` と `次に見る条件` を確認する
- `方向の強さ` `実行しやすさ` `待機圧力` は補強材料として読む

## 今回の狙い

- `上方向バイアス` が先頭に来て「今すぐロングしたい」と誤読されやすい形を減らす
- `上目線だが今は待つ` を件名・本文・詳細 HTML で同じ意味順に見せる
- あとで `evaluation_trace` とレビュー結果を照らし、件名や本文の誤読を分析しやすくする

## 変更対象

- `src/presentation/sanitize.py`
- `src/ai/summary.py`
- `src/notification/detail_page.py`
- `src/analysis/evaluation_trace.py`
- `main.py`

## 運用上の注意

- `notification_context` は表示用の派生値です。通知判定の閾値そのものはここでは変えていません。
- 通知文面を直すときは、件名だけ・本文だけを個別に直さず、まず `notification_context` で必要項目を足す方針を優先します。
