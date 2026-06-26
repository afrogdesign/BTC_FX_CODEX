# analysis

このディレクトリには、ChatGPT が行う診断、考察、改善案比較のレポートを保存します。

ここに置く文書は、まだ実装仕様として確定していない分析・仮説・比較検討のための資料です。

## 保存するもの

- ログやレポートの読解結果
- 原因仮説
- 改善案の比較
- gate や score の再設計案
- Codex に追加調査を依頼するための整理

## 保存しないもの

- Codex にそのまま実装させる確定仕様
- 実装済みコードの説明だけの文書
- 秘密情報
- `.env` の内容
- APIキー、秘密鍵、個人情報

## 命名規則

```txt
YYYYMMDD_topic.md
```

例:

```txt
20260526_sl_hit_redesign.md
20260526_trend_flip_review.md
```

## 現在の継続メモ

- `20260526_entry_sl_tp_wait_redesign.md`
- `20260526_trend_flip_confirmed_up_reassessment.md`

`chatgpt/specs/active/` が空のとき、ChatGPT は `NEXT_TASK.md` と `report_hub_latest.md` を見たあと、まずこの2本を起点に次の設計を進める。

## specs との違い

`analysis/` は考察用です。
`chatgpt/specs/active/` は確定仕様用です。

分析が終わり、実装方針が固まったものだけを `chatgpt/specs/active/` に移してください。
