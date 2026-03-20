# 外部AIレビュー用部品一式
更新日: 2026-03-17 01:14 JST

このフォルダは、`2026-03-17 01:14 JST` の本番 `CLI` 成功ログをもとに、
「通知本文をもっと読みやすくできるか」を別AIに相談するための部品をまとめたものです。

## 使い方
- まず [external_ai_review_prompt.md](./external_ai_review_prompt.md) をそのまま別AIへ渡してください。
- 必要に応じて、元資料として次の 3 ファイルも参照してください。
- [summary_system_prompt.md](./summary_system_prompt.md)
- [summary_result_payload.json](./summary_result_payload.json)
- [summary_current_output.md](./summary_current_output.md)

## この一式に入っているもの
- `summary_system_prompt.md`
  - 現在の通知本文用 system prompt です。
- `summary_result_payload.json`
  - 実際に通知本文生成へ渡した JSON データです。
- `summary_full_prompt.txt`
  - ラッパーが実際に AI へ渡す完成形の入力です。
- `summary_current_output.md`
  - 現在の出力本文です。
- `external_ai_review_prompt.md`
  - 別AIに改善相談するときの、そのまま使える依頼文です。
- `advice_system_prompt.md`
  - 参考用です。本文生成の前段にある AI 審査 prompt です。

## 補足
- 今回の主目的は「通知本文の読みやすさ改善」なので、中心は summary 側です。
- `advice_system_prompt.md` は、前段の AI 判断もあわせて見たいときだけ使ってください。
- API キーなどの秘密情報は含めていません。
