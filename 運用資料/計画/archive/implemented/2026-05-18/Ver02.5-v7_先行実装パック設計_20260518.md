# Ver02.5-v7 先行実装パック設計

更新日: 2026-05-18 JST

## 目的

正式な Phase 1B / 自動売買へ進む前に、通知の「入る価格」の粗さを減らす。評価軸は後から再調整できる前提で、今回は危ない `ready` を減らし、検証材料を増やす。

## 実装対象

- `15分足 執行精度チェック`
  - 主要サポート直近の short は `wait_only` とし、`ready` なら `watch` へ落とす。
  - 主要レジスタンス直近の long は `wait_only` とし、`ready` なら `watch` へ落とす。
  - 上抜け後の支持化が残る short、下抜け後の抵抗化が残る long は無効寄りの待機扱いにする。
  - ブレイク追随候補は `breakout_follow_candidate` として記録するが、正式 gate 通過には使わない。

- `market_map` の非対称評価
  - `trend_flip_confirmed_down` は従来どおり下方向材料として扱う。
  - `trend_flip_confirmed_up` は弱い確認材料として扱い、long 加点を `+2`、short 減点を `-3` に縮小する。
  - 通知文言は「上方向転換は慎重評価。押し目保持と1時間足継続まで待つ」に寄せる。

- 表示と保存
  - 詳細HTMLのロング/ショート再検討ラインに `15分足 執行チェック` を表示する。
  - CSV / result に `execution_precision_action`, `execution_precision_flags`, `execution_precision_reason` を保存する。
  - `SYSTEM_LABEL` は `Ver02.5-v7` に更新する。

## 現在の観測値

- daily 評価: 47 件
- 概算 PF: 0.73
- 勝率: 46.8%
- formal pass: 0 件
- Phase1B-lite: 5 件
- `trend_flip_confirmed_up`: 弱く、強材料として扱うには不十分
- `support_to_resistance_flip`: 有効性が比較的高く、下方向材料として継続観測

## 完了条件

- 主要ライン直近の追いかけ `ready` が `watch` に落ちる。
- `breakout_follow_candidate` は記録されるが、正式 gate は上がらない。
- 詳細HTMLで 15分足の執行判断を読める。
- CSV に執行精度チェック結果が残る。
- ロードマップと計画タイムラインに `Ver02.5-v7` の現在地が反映される。

## テスト観点

- short が主要サポート直近なら `execution_precision_wait_only` になる。
- long が主要レジスタンス直近なら `execution_precision_wait_only` になる。
- `trend_flip_confirmed_up` の score 影響が弱いことを確認する。
- 詳細HTMLに `15分足 執行チェック` が表示される。
- 全体テストは `./.venv312/bin/python -m unittest discover -s tests` で確認する。
