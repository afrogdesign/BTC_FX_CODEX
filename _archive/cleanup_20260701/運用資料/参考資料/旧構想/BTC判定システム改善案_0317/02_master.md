# ⭕️BTC判定システム 改善マスターパック

## 0. この文書の役割
この文書は、`afrogdesign/BTC_FX_CODEX` に対して、**評価ロジック改善の正式文書を repo に配置し、次の実装に進むための基準点を作る** ためのマスター資料です。

この1本に、次をまとめています。

- repo に置くべき正式仕様の骨子
- 保存先パスの提案
- `NEXT_TASK.md` / `progress.md` の追記方針
- 実装タスク分解
- ブランチ / コミット / PR の提案

---

## 1. 保存先パスの提案

### 第一候補
`運用資料/計画/評価システム改善仕様書_Ver02x-Ver05接続.md`

### 理由
- `運用資料/` 直下は横断管理ファイルが多い
- `運用資料/計画/` にはフェーズ別計画やマイルストーン定義がまとまっている
- 今回の文書は「一時メモ」ではなく、**Ver02.x から Ver05 へ繋ぐ正式な改善計画文書** に当たる

### 置かない方がよい場所
- repo 直下
- `docs/` が無い場合の新設
- `src/` 配下
- `tests/` 配下

---

## 2. repo に配置する正式仕様書の骨子

以下の内容で、`運用資料/計画/評価システム改善仕様書_Ver02x-Ver05接続.md` を作る想定です。

### 2-1. 文書タイトル案
`# ⭕️評価システム改善仕様書_Ver02x-Ver05接続`

### 2-2. 目的
- 現行のBTC判定システムの最終挙動を大きく崩さずに、評価ロジック改善のための観測基盤を先に整備する
- Ver03 / Ver04 / Ver05 へ自然に接続できるよう、shadow 指標・理由コード・比較可能なログ構造を導入する
- 改善判断を感覚ではなく、比較可能な記録に基づいて行える状態を作る

### 2-3. 現在地
- Ver02.1 / Phase 0 実運用確認中
- 並行して Phase 1 損益管理モジュール導入準備あり
- 本仕様は Ver02.x 時点で導入可能な **観測基盤整備** を対象とする

### 2-4. 今回の対象範囲
- 評価ロジックの観測可能性向上
- `result` / JSON ログへの `evaluation_trace` ブロック追加検討
- shadow 指標の定義
- 理由コード整備
- テスト観点の明文化
- 将来フェーズとの接続定義

### 2-5. 今回の非対象範囲
- 最終シグナル閾値の本格調整
- 通知条件の大幅変更
- `build_setup()` の全面改修
- prelabel の正式な内部連続値化
- A/B 比較モードの本実装
- 大規模なコード書き換え

### 2-6. 基本方針
- 既存の最終判定は当面維持する
- 先に内部観測値を追加し、比較可能なログを整備する
- 本番挙動を変える前に、shadow 値として保存・観測する
- 変更は 1 フェーズ 1 意図で進める
- 通知件数だけを理由に閾値調整しない

---

## 3. 追加したい shadow 指標

### 推奨項目
- `evaluation_trace_version`
- `direction_score_shadow`
- `entry_quality_score_shadow`
- `trigger_quality_score_shadow`
- `trigger_reason_codes`
- `risk_component_scores`
- `confidence_components`
- `setup_decision_reason_codes`
- `signal_tier_inputs_summary`

### 設計意図
#### `direction_score_shadow`
純粋な方向感を観測する。  
「上か下か」を、エントリー位置の良し悪しと少し切り離して見るための補助値。

#### `entry_quality_score_shadow`
「いまその位置で入る質」を観測する。  
方向感が合っていても、位置が悪いケースを分離して観測する。

#### `trigger_quality_score_shadow`
直近発火条件の質を観測する。  
ブレイク、出来高、オーダーフロー、板要因などのうち、どの成分が trigger_ready に寄与しているかを後で比較できるようにする。

#### `trigger_reason_codes`
trigger 判定の理由コード。  
将来 `build_setup()` を精密化する前段として、判断根拠を記録する。

#### `risk_component_scores`
`position_risk` の内訳。  
例:
- `sweep_risk_score`
- `chase_risk_score`
- `fake_break_risk_score`
- `thin_liquidity_risk_score`

#### `confidence_components`
confidence の内訳。  
例:
- `trend_component`
- `structure_component`
- `rr_component`
- `risk_penalty`
- `data_quality_penalty`

#### `setup_decision_reason_codes`
最終セットアップ可否の理由コード。  
どの減点・抑制が最終 decision に効いたかを残す。

#### `signal_tier_inputs_summary`
`compute_signal_tier` に渡る主要入力の要約。  
tier 判定の再現性を上げる。

---

## 4. 保存形式の推奨

### 基本方針
- **JSON を正本**
- CSV は代表列のみにとどめる
- まずは `result` / `last_result.json` / signal ログで持つ
- トップレベルに大量展開せず、`evaluation_trace` という親キー配下にまとめる方向を優先する

### 推奨イメージ
```json
{
  "evaluation_trace": {
    "version": "v0.1",
    "direction_score_shadow": 72,
    "entry_quality_score_shadow": 41,
    "trigger_quality_score_shadow": 58,
    "trigger_reason_codes": ["breakout_up", "volume_expand"],
    "risk_component_scores": {
      "sweep_risk_score": 68,
      "chase_risk_score": 45,
      "fake_break_risk_score": 39,
      "thin_liquidity_risk_score": 22
    },
    "confidence_components": {
      "trend_component": 28,
      "structure_component": 18,
      "rr_component": 12,
      "risk_penalty": -14,
      "data_quality_penalty": -4
    },
    "setup_decision_reason_codes": ["rr_insufficient", "critical_zone_warning"],
    "signal_tier_inputs_summary": {
      "bias": "long",
      "confidence": 61,
      "prelabel": "SWEEP_WAIT",
      "warning_count": 3
    }
  }
}
```

### 補足
`shadow_log.csv` を導入する場合は **新設予定** と明記し、最初から必須前提にはしない。  
まずは JSON 正本で設計する。

---

## 5. `NEXT_TASK.md` 追記案

以下のような粒度が適切です。

### 追記案
- 評価システム改善仕様書を `運用資料/計画/` 配下に正式配置
- `evaluation_trace` の最小構造案を確定
- `compute_scores` / `evaluate_position_risk` / `compute_confidence` / `build_setup` / `compute_signal_tier` の shadow 観測項目を洗い出す
- 評価コア単体テストの追加方針を決める
- 過去ログ比較用の軽量レポート案を作る

---

## 6. `progress.md` 追記案

### 追記の主旨
- 今回の作業は「本番判定変更」ではなく「観測基盤整備」である
- Ver02.x の現在地を維持しつつ、Ver03 / Ver05 の改善準備を開始した
- 正式仕様書を配置し、今後のコード改修判断の基準点を作った

### 追記サンプル
- 評価システム改善仕様書を新規整備し、Ver02.x では shadow 指標中心で進める方針を確定
- `evaluation_trace` を軸とした比較可能なログ設計を検討開始
- 次工程として、shadow 返却項目の設計 → 保存接続 → 単体テスト → 比較レポートの順で進める

---

## 7. 実装タスク分解

### Phase A: 文書整備
- 正式仕様書を配置
- `NEXT_TASK.md` 更新
- `progress.md` 更新

### Phase B: shadow 指標の返却追加
- 評価コアの返却項目を洗い出す
- 関数ごとに shadow 値や理由コードを返せる形を設計する
- 既存挙動を変えない形で追加する

### Phase C: `evaluation_trace` 保存接続
- `result` への格納位置を決める
- JSON ログへの保存を追加する
- トップレベル展開を避ける

### Phase D: 評価コア単体テスト
- `compute_scores`
- `evaluate_position_risk`
- `compute_confidence`
- `build_setup`
- `compute_signal_tier`

上記のテスト観点を追加する

### Phase E: 比較レポート整備と将来接続準備
- 過去ログと shadow 値の比較レポート案を作る
- Ver05 の A/B 比較や prelabel 内部スコア化へ接続できるようにする

---

## 8. 完了条件

### 今回の文書整備完了条件
- 正式仕様書が repo の適切な場所に配置されている
- `NEXT_TASK.md` に次作業が追記されている
- `progress.md` に今回の意味づけが記録されている
- 実装タスクが Phase 単位で整理されている
- 後から見返しても、次の担当者が迷わず着手できる

### 今回はまだ完了条件に含めないもの
- shadow 指標の本実装
- テストの全追加
- 比較レポートの完成
- 閾値調整
- 最終シグナル仕様の変更

---

## 9. ブランチ / コミット / PR 提案

### ブランチ名案
`docs/eval-spec-v02x-v05`

### コミットメッセージ案
```text
docs: 評価システム改善仕様書（Ver02.x〜Ver05接続版）を追加
```

```text
docs: NEXT_TASKとprogressに評価改善の計画を追記
```

### PRタイトル案
```text
評価システム改善仕様書（Ver02.x〜Ver05接続版）を追加
```

### PR本文の要旨
- 評価システム改善仕様書を正式配置
- 現行判定を壊さず、shadow 指標ベースで観測基盤を整備する方針を明文化
- `NEXT_TASK.md` と `progress.md` を更新
- Ver03 / Ver04 / Ver05 に接続するための実装導線を整理

---

## 10. 最終メモ
今回の核心は、**評価改善そのものを今すぐ完成させることではなく、改善を正しく進めるための比較可能な基準点を repo に残すこと** です。  
この文書は、そのための正本候補です。
