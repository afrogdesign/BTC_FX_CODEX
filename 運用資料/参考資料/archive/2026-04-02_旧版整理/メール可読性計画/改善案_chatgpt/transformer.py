import json
from pathlib import Path

# このサンプルは、今回の実データ構造を前提にした最小版です。
# 必要に応じて label 関数や flag マッピングを拡張してください。

def fmt_num(n, digits=2):
    return f"{n:,.{digits}f}"

# 実装本体は配布パッケージの semantic_output_sample.json を見本にしてください。
# ここでは読み込みと書き出しの最小例のみ載せています。

def main():
    src = Path('sample_input.json')
    dst = Path('semantic_output.json')
    raw = json.loads(src.read_text(encoding='utf-8'))

    semantic = {
  "summary_version": "v1",
  "market": "BTCUSDT",
  "timestamp_jst": "2026-03-17T01:14:15.408472+09:00",
  "headline": {
    "entry_judgement": "待機優先",
    "position_label": "今は入る位置が悪い",
    "direction_label": "ロング寄り",
    "phase_label": "押し目・戻り待ち",
    "confidence_label": "中高め",
    "confidence_score": 71
  },
  "direction": {
    "bias": "long",
    "bias_label": "ロング寄り",
    "market_regime": "uptrend",
    "market_regime_label": "上昇基調",
    "phase": "pullback",
    "phase_label": "押し目・戻り待ち",
    "timeframe_view": {
      "4h": "ロング優勢",
      "1h": "ロング優勢",
      "15m": "様子見"
    },
    "score_summary": {
      "long": 100,
      "short": 29,
      "gap": 71,
      "dominance_label": "ロング優勢"
    }
  },
  "current_state": {
    "current_price": 73240.2,
    "current_price_label": "73,240.20 USDT",
    "location_character": "サポート帯とレジスタンス帯が重なる不安定な位置",
    "critical_zone": true,
    "location_risk": 100.0,
    "location_risk_label": "非常に高い"
  },
  "market_conditions": {
    "funding": "ほぼ中立 (+0.0020%)",
    "volatility_label": "やや高め",
    "volume_label": "やや弱い",
    "oi_label": "やや増加",
    "cvd_label": "やや強気",
    "orderbook_label": "売り板優勢"
  },
  "zones": {
    "nearest_support": {
      "range": "73,080.89 - 73,243.11",
      "distance": 0.0,
      "label": "直下のサポート帯"
    },
    "second_support": {
      "range": "72,774.89 - 73,032.81",
      "distance": 207.39,
      "label": "次のサポート帯"
    },
    "nearest_resistance": {
      "range": "73,094.29 - 73,256.51",
      "distance": 0.0,
      "label": "直上のレジスタンス帯"
    },
    "second_resistance": {
      "range": "73,722.49 - 74,116.11",
      "distance": 482.29,
      "label": "次のレジスタンス帯"
    }
  },
  "liquidity_context": {
    "below_liquidity_price": 73144.0,
    "above_liquidity_price": 73544.3,
    "nearest_liquidity_label": "下の流動性が近い",
    "sweep_status": "未完了",
    "sweep_label": "先に下を掃除する可能性あり",
    "liquidation_label": "清算ポイントが現在値の近くにある"
  },
  "setups": {
    "long": {
      "status": "監視候補",
      "entry_zone": "73,080.89 - 73,243.11",
      "stop": 72472.57,
      "tp1": 73722.49,
      "tp2": 74540.86,
      "rr_label": "利益幅が不足気味"
    },
    "short": {
      "status": "条件不足",
      "entry_zone": "73,094.29 - 73,256.51",
      "stop": 73864.83,
      "tp1": 73032.81,
      "tp2": 71796.54,
      "rr_label": "利益幅が不足気味"
    }
  },
  "risks": {
    "primary_reason": "下の流動性が近く、まだスイープ未完了",
    "risk_labels": [
      "重要ゾーン内で不安定",
      "リスクリワードが弱い",
      "ロングの利益幅が不足気味",
      "ショートの利益幅が不足気味",
      "上に売り板が近い",
      "CVDはやや強気",
      "下に流動性が近い",
      "売り板が優勢",
      "まだ下振れ余地がある"
    ]
  },
  "final_message_guide": {
    "one_line_conclusion": "全体はロング寄りですが、現在地が不安定なため今は待機優先です。",
    "action_hint": "下を振って反発するか、上抜け後に押し目を作るまで待つのが自然です。"
  }
}

    dst.write_text(json.dumps(semantic, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'written: {dst}')

if __name__ == '__main__':
    main()
