# ⭕️自然文レポート変換パッケージ

この一式は、機械判定向けの相場JSONを、読みやすい日本語レポートへ変換するための最小構成です。

## 入っているもの

- `sample_input.json` : 実際に受け取った元データのサンプル
- `semantic_output_sample.json` : 自然文生成用に整理した中間データ
- `natural_report_sample.md` : 中間データから生成した自然文サンプル
- `natural_report_schema.json` : 中間データのJSONスキーマ
- `field_mapping.md` : 元データ → 意味データの変換表
- `prompt_template.md` : 文章生成AIへ渡すためのテンプレート
- `transformer.py` : 生データから中間データを作るPythonサンプル

## 推奨フロー

1. 生データJSONを受け取る
2. `transformer.py` で意味データへ変換する
3. `prompt_template.md` の指示文と一緒にAIへ渡す
4. 読みやすい相場レポートを生成する

## 重要な考え方

生データをそのままAIへ渡すと、

- 数字が多すぎる
- 同じ意味の情報が分散する
- 文章の優先順位がブレる

という問題が出やすいです。

そのため、先に「意味データ」に変換してから文章化する構成にしています。
