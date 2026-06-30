# FXシステム AIやりとり完全フロー やさしい版 Obsidian用

更新日: 2026-03-30 JST

この資料は、FX監視システムの中で、AI がどこで呼ばれて、何を見て、何を返し、その結果がどこへ残るかを、できるだけやさしく見える化したものです。
Obsidian の Mermaid 表示を前提にしています。

## 1. まず全体像

```mermaid
flowchart TD
    A["定時になる"] --> B["システム開始<br>`main.py`"]
    B --> C["相場データを集める"]
    C --> D["機械の判断をまとめる<br>`core_result`"]
    D --> E["AIに相談する<br>`src/ai/advice.py`"]
    E --> F["AIの返事を受け取る"]
    F --> G["通知するか決める<br>`src/notification/trigger.py`"]
    G --> H["件名と本文を作る"]
    H --> I["メール送信 または 保存だけ"]
    I --> J["結果を JSON / CSV に残す"]
    J --> K["あとで人がレビューする"]
```

## 2. AIとの会話だけを抜き出すと

```mermaid
flowchart LR
    A["機械の判断をまとめたデータ<br>`core_result`"] --> B["AI相談口<br>`src/ai/advice.py`"]
    B --> C{"相談方法"}
    C -->|CLI| D["`tools/codex_cli_wrapper.py`"]
    C -->|API| E["OpenAI API"]
    D --> F["AIへ質問を送る"]
    E --> F
    F --> G["AIの返事<br>売買判断 / 自信度 / 理由 / 注意点"]
    G --> H["システム側で形を整える<br>`_normalize_advice()`"]
    H --> I["結果を `core_result.ai_advice` に入れる"]
```

## 3. AIに渡しているもの

難しく言うと構造化データですが、実際には次のような「機械が先に調べた結果」をまとめて渡しています。

```mermaid
flowchart TD
    A["AIに渡す材料"] --> B["今の価格"]
    A --> C["上目線か 下目線か 様子見か"]
    A --> D["いま入りやすい位置か"]
    A --> E["危険サインがあるか"]
    A --> F["ロング案とショート案"]
    A --> G["相場の流れ"]
    A --> H["補助説明文<br>`build_qualitative_context()`"]
```

## 4. AIから返ってくるもの

```mermaid
flowchart TD
    A["AIの返事"] --> B["どうする判断<br>買い寄り / 売り寄り / 待つ / 見送り"]
    A --> C["自信度"]
    A --> D["理由"]
    A --> E["注意点"]
    A --> F["次に何を待つか"]
    B --> G["`core_result.ai_decision`"]
    C --> H["`core_result.ai_confidence`"]
    D --> I["`core_result.ai_advice.primary_reason`"]
    E --> J["`core_result.ai_advice.warnings`"]
    F --> K["`core_result.ai_advice.next_condition`"]
```

## 5. 実際の会話の順番

```mermaid
sequenceDiagram
    participant Sys as システム
    participant Main as main.py
    participant Advice as src/ai/advice.py
    participant AI as CLI または API
    participant Notify as 通知判定
    participant Save as 保存処理

    Sys->>Main: 定時実行
    Main->>Main: 相場データを集めて機械判断を作る
    Main->>Advice: AIに相談する
    Advice->>AI: 判断材料を送る
    AI-->>Advice: 判断 / 理由 / 注意点を返す
    Advice-->>Main: 整えた結果を返す
    Main->>Notify: 通知するか判定
    Notify-->>Main: 通知する / しない
    Main->>Save: 件名・本文・結果を保存
```

## 6. 通知までの流れ

```mermaid
flowchart TD
    A["AIの返事を受け取る"] --> B["通知ランクを決める"]
    B --> C["前回と比べる<br>`logs/last_result.json` など"]
    C --> D["通知する価値があるか決める"]
    D --> E{"送る?"}
    E -->|はい| F["メール件名を作る"]
    E -->|いいえ| G["送らず保存だけ"]
    F --> H["メール本文を作る"]
    H --> I["送信する"]
    I --> J["送信結果を保存"]
    G --> J
```

## 7. 最後にどこへ残るか

```mermaid
flowchart TD
    A["1回分の結果"] --> B["最新結果<br>`logs/last_result.json`"]
    A --> C["通知した最新結果<br>`logs/last_notified.json`"]
    A --> D["注意報の最新結果<br>`logs/last_attention_notified.json`"]
    A --> E["1件ごとの保存<br>`logs/signals/signal_id.json`"]
    A --> F["表でたまる記録<br>`logs/csv/trades.csv`"]
    A --> G["失敗記録<br>`logs/errors/*.log`"]
    F --> H["人のレビュー入力<br>`tools/log_feedback.py`"]
    H --> I["レビュー保存<br>`logs/review/review_form_state.json`"]
```

## 8. これを一言で言うと

```text
相場データを集める
→ 機械が先に判断する
→ AIが意味づけする
→ 通知するか決める
→ 件名と本文を作る
→ 結果を保存する
→ あとで人が見直す
```

## 9. 非エンジニア向けの理解ポイント

- AI は最初から全部を考えているわけではありません。
- 先にシステムが数字や状態を整理し、その整理済みデータを AI に渡しています。
- AI の主な役割は「意味づけ」と「人が読める判断補助」です。
- AI が返した内容は、そのまま終わらず、通知判断や保存データにも使われます。
- つまりこの仕組みは、`機械判断 + AI補足 + 人レビュー` の3段で回っています。
