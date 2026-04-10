更新日: 2026-04-10 05:30 JST

# 通知共通層 `notification_context` メモ

このメモは、通知の見え方をそろえるための表示層 `notification_context` を短く確認するための実務メモです。  
現行は `Ver02.4-v1` で使っています。

## まず結論

- `notification_context` は、通知を `方向のお知らせ` ではなく `行動判断の補助` として見せるための共通表示層です。
- 判定ロジック本体は別にあり、ここでは `bias` `prelabel` `primary_setup_status` `notification_kind` `flags` などを通知向けの日本語に変換します。
- 件名、本文、詳細 HTML、`evaluation_trace` ができるだけ同じ意味順で読めるようにするのが役目です。

## 今の役割

- `いま注目すべきか`
- `いま入るのか、待つのか`
- `どの価格帯を主に見るのか`
- `次に何を確認すれば判断が進むか`

この4点を、通知の最初の数行で伝えるために使います。

## 主な項目

- `status_code`
  - `attention` `monitor` `actionable` `invalid` `neutral`
- `status_label`
  - `注意報` `監視` `執行可` `無効` `中立`
- `status_explanation`
  - いまの通知をどう受け取るべきかの短い説明
- `execution_label`
  - `見送り` `監視継続` `条件付きで検討`
- `entry_window_label`
  - どの価格帯なら検討対象になるか
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
  - 想定 RR の短い要約
- `price_map`
  - サポート、レジスタンス、再検討帯、`SL/TP` の表示材料

## 今の読み方

1. `status_label` と `execution_label` を先に見る
2. `entry_window_label` で、どの価格帯を待つのか確認する
3. `reason_labels` で、その判断の主理由を読む
4. 詳細 HTML では `15分足` を主役にして、`入る価格 / SL / TP` を見る

## 現在の注意点

- `最終ランク` が高くても、即エントリー可とは限りません
- `notification_context` は「通知の優先度」と「実行可否」を読み違えにくくするためにあります
- 価格精度の改善そのものは `notification_context` ではなく、`RR` `position_risk` `AI事後評価` 側で行います

## このメモを見る場面

- 件名や本文が誤読されやすいと感じたとき
- 詳細 HTML とメール本文で意味がずれて見えるとき
- `misleading_entry_like_wording` の原因を探すとき

## 変更対象

- `src/presentation/sanitize.py`
- `src/ai/summary.py`
- `src/notification/detail_page.py`
- `src/analysis/evaluation_trace.py`
- `main.py`

## 運用上の注意

- `notification_context` は表示用の派生値です。通知判定の閾値そのものはここで変えていません。
- 通知文面を直すときは、件名だけ・本文だけを個別に触るより、まず `notification_context` で意味順を整える方針を優先します。
