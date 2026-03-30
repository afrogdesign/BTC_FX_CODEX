from __future__ import annotations

import html
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.presentation.sanitize import (
    CONFIDENCE_METRIC_LABELS,
    build_display_context,
    sanitize_flag_list,
    sanitize_user_text,
)


_SETUP_STATUS_LABELS = {
    "ready": "条件付きで検討",
    "watch": "監視継続",
    "invalid": "現状は見送り",
    "none": "未形成",
}

_REGIME_LABELS = {
    "uptrend": "上昇基調",
    "downtrend": "下降基調",
    "range": "レンジ",
    "volatile": "値動きが荒い状態",
    "transition": "転換帯",
}

_PHASE_LABELS = {
    "trend_following": "トレンド継続",
    "pullback": "押し目・戻り待ち",
    "breakout": "ブレイク局面",
    "range": "レンジ局面",
    "reversal_risk": "反転注意",
}

_SIGNAL_LABELS = {
    "long": "ロング優勢",
    "short": "ショート優勢",
    "wait": "様子見",
}


def _format_price(value: Any) -> str:
    try:
        return f"{float(value):,.2f}"
    except (TypeError, ValueError):
        return str(value or "未記録")


def _format_pct(value: Any) -> str:
    try:
        return f"{float(value):+.4f}%"
    except (TypeError, ValueError):
        return str(value or "未記録")


def _setup_status_label(value: Any) -> str:
    return _SETUP_STATUS_LABELS.get(str(value or "").lower(), "未形成")


def _label_regime(value: Any) -> str:
    return _REGIME_LABELS.get(str(value or "").lower(), str(value or "未記録"))


def _label_phase(value: Any) -> str:
    return _PHASE_LABELS.get(str(value or "").lower(), str(value or "未記録"))


def _label_signal(value: Any) -> str:
    return _SIGNAL_LABELS.get(str(value or "").lower(), str(value or "未記録"))


def _metric_hint(metric_key: str, value: Any) -> str:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return "未記録"
    if metric_key == "direction":
        if score >= 80:
            return "かなり強い"
        if score >= 60:
            return "強め"
        if score >= 40:
            return "中くらい"
        return "弱め"
    if metric_key == "execution":
        if score >= 70:
            return "今も入りやすい"
        if score >= 40:
            return "条件つき"
        return "今は入りにくい"
    if score >= 70:
        return "かなり待ち寄り"
    if score >= 40:
        return "待ち優先"
    return "待機圧力は低め"


def _metric_help(metric_key: str) -> str:
    if metric_key == "direction":
        return "相場の向きそのものが、どれだけはっきりしているかを表します。高いほど方向判断に迷いが少ない状態です。"
    if metric_key == "execution":
        return "今この価格で実際に入る条件がどれだけ整っているかを表します。方向が合っていても、ここが低いなら飛びつきは不利です。"
    return "今は待ったほうがよい圧力の強さです。高いほど、方向は見えていてもタイミングはまだという意味になります。"


def _zone_summary(name: str, zones: list[dict[str, Any]]) -> str:
    if not zones:
        return f"{name}: 目立つ価格帯は抽出なし"
    parts: list[str] = []
    for zone in zones[:2]:
        low = _format_price(zone.get("low"))
        high = _format_price(zone.get("high"))
        distance = _format_price(zone.get("distance_from_price"))
        parts.append(f"{low} - {high}（現在値から {distance} ドル）")
    return f"{name}: " + " / ".join(parts)


def _setup_line(result: dict[str, Any], side: str) -> str:
    setup = result.get("long_setup", {}) if side == "long" else result.get("short_setup", {})
    label = "ロング" if side == "long" else "ショート"
    return (
        f"{label}: {_setup_status_label(setup.get('status'))}。"
        f" 再検討帯 {_format_price((setup.get('entry_zone') or {}).get('low'))} - {_format_price((setup.get('entry_zone') or {}).get('high'))}"
        f" / 損切り目安 {_format_price(setup.get('stop_loss'))}"
        f" / TP1 {_format_price(setup.get('tp1'))}"
        f" / TP2 {_format_price(setup.get('tp2'))}"
    )


def _build_wait_reasons(display_context: dict[str, Any], result: dict[str, Any]) -> list[str]:
    reasons = [str(item) for item in display_context.get("wait_reason_labels", []) if str(item).strip()]
    if reasons:
        return reasons
    ai_advice = result.get("ai_advice")
    if isinstance(ai_advice, dict):
        return sanitize_flag_list(ai_advice.get("warnings", []))
    return ["大きな待機理由は出ていません"]


def _raw_mail_text(result: dict[str, Any], display_context: dict[str, Any]) -> str:
    metric_labels = display_context.get("confidence_metric_labels", CONFIDENCE_METRIC_LABELS)
    lines = [
        "【結論】",
        f"方向判断: {display_context.get('direction_label', '')}",
        f"いまの扱い: {display_context.get('action_label', '')}",
        f"{metric_labels['direction']}: {result.get('confidence_direction_shadow', '')}",
        f"{metric_labels['execution']}: {result.get('confidence_execution_shadow', '')}",
        f"{metric_labels['wait']}: {result.get('confidence_wait_shadow', '')}",
        f"位置評価: {display_context.get('entry_quality_label', '')}",
    ]
    return "\n".join(lines)


def build_notification_detail_html(result: dict[str, Any]) -> str:
    display_context = build_display_context(result)
    metric_labels = display_context.get("confidence_metric_labels", CONFIDENCE_METRIC_LABELS)
    timestamp_jst = str(result.get("timestamp_jst", "")).replace("T", " ")
    subject = str(result.get("summary_subject", "")).strip() or f"{display_context.get('direction_compact_label', '中立')} / {display_context.get('action_compact_label', '見送り')}"
    wait_reasons = _build_wait_reasons(display_context, result)
    ai_advice = result.get("ai_advice") if isinstance(result.get("ai_advice"), dict) else {}
    ai_reason = sanitize_user_text(ai_advice.get("primary_reason") or ai_advice.get("notes") or "")
    ai_next = sanitize_user_text(ai_advice.get("next_condition", ""))
    ai_warnings = sanitize_flag_list(ai_advice.get("warnings", []))
    funding_display = str(result.get("funding_rate_display") or "").strip() or f"{result.get('funding_rate_label', 'ほぼ中立')} ({_format_pct(result.get('funding_rate_pct', 0.0))})"
    summary_chips = [
        display_context.get("direction_compact_label", "中立"),
        display_context.get("action_compact_label", "見送り"),
        display_context.get("entry_quality_label", "内部評価あり"),
    ]

    def esc(value: Any) -> str:
        return html.escape(str(value or "未記録"))

    def chips_html(items: list[str], class_name: str = "chip") -> str:
        return "".join(f'<span class="{class_name}">{esc(item)}</span>' for item in items if str(item).strip())

    metric_blocks: list[str] = []
    for key, value in (
        ("direction", result.get("confidence_direction_shadow")),
        ("execution", result.get("confidence_execution_shadow")),
        ("wait", result.get("confidence_wait_shadow")),
    ):
        metric_blocks.append(
            '<div class="metric-card">'
            f'<div class="metric-label">{esc(metric_labels[key])}</div>'
            f'<div class="metric-value">{esc(value)}</div>'
            f'<div class="metric-hint">{esc(_metric_hint(key, value))}</div>'
            f'<p>{esc(_metric_help(key))}</p>'
            "</div>"
        )

    root_cards = [
        ("方向判断", display_context.get("direction_label", "")),
        ("いまの扱い", display_context.get("action_label", "")),
        ("位置評価", display_context.get("entry_quality_label", "")),
        ("総合判断", _label_signal(result.get("bias"))),
        ("相場環境", _label_regime(result.get("market_regime"))),
        ("局面", _label_phase(result.get("phase"))),
        (
            "時間軸",
            f"4時間足 {_label_signal(result.get('signals_4h'))} / 1時間足 {_label_signal(result.get('signals_1h'))} / 15分足 {_label_signal(result.get('signals_15m'))}",
        ),
        (
            "スコア差",
            f"ロング {result.get('long_display_score')} / ショート {result.get('short_display_score')} / 差 {result.get('score_gap')}",
        ),
    ]
    root_cards_html = "".join(
        '<div class="fact-card">'
        f"<h3>{esc(label)}</h3>"
        f"<p>{esc(value)}</p>"
        "</div>"
        for label, value in root_cards
    )

    wait_reason_html = "".join(f"<li>{esc(reason)}</li>" for reason in wait_reasons)
    ai_warning_html = "".join(f"<li>{esc(reason)}</li>" for reason in ai_warnings)
    raw_mail = _raw_mail_text(result, display_context)

    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(subject)}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f4f6f8;
      --paper: #ffffff;
      --ink: #10212b;
      --muted: #60707c;
      --line: #d8dfe6;
      --accent: #0f766e;
      --accent-soft: #dff7f2;
      --warn: #b45309;
      --sky: #e0f2fe;
      --shadow: 0 10px 30px rgba(16, 33, 43, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Hiragino Sans", "Yu Gothic", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, #d8f3ff 0%, transparent 32%),
        linear-gradient(180deg, #f6fbff 0%, var(--bg) 45%, #eef2f6 100%);
      line-height: 1.75;
    }}
    .wrap {{ max-width: 1100px; margin: 0 auto; padding: 28px 18px 56px; }}
    .hero, .section {{
      background: rgba(255, 255, 255, 0.94);
      border: 1px solid rgba(216, 223, 230, 0.9);
      border-radius: 22px;
      box-shadow: var(--shadow);
      margin-bottom: 18px;
    }}
    .hero {{
      padding: 28px;
      background:
        linear-gradient(135deg, rgba(224, 242, 254, 0.92) 0%, rgba(255,255,255,0.96) 48%, rgba(223,247,242,0.96) 100%);
    }}
    .section {{ padding: 22px; }}
    h1, h2, h3 {{ margin: 0 0 10px; line-height: 1.4; }}
    h1 {{ font-size: 30px; letter-spacing: 0.01em; }}
    h2 {{ font-size: 21px; }}
    h3 {{ font-size: 15px; color: var(--muted); }}
    p {{ margin: 0 0 10px; }}
    .muted {{ color: var(--muted); font-size: 14px; }}
    .chip {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 7px 12px;
      border-radius: 999px;
      border: 1px solid rgba(15, 118, 110, 0.12);
      background: rgba(255,255,255,0.84);
      color: var(--ink);
      font-size: 13px;
      font-weight: 700;
      margin: 0 8px 8px 0;
    }}
    .hero-grid, .fact-grid, .metric-grid, .two-col {{
      display: grid;
      gap: 14px;
    }}
    .hero-grid {{ grid-template-columns: 1.4fr 1fr; margin-top: 18px; }}
    .fact-grid {{ grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); }}
    .metric-grid {{ grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); }}
    .two-col {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    .panel {{
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 16px;
      background: #fbfdfe;
    }}
    .fact-card {{
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 16px;
      background: linear-gradient(180deg, #ffffff 0%, #f9fbfc 100%);
    }}
    .fact-card p {{ font-size: 18px; font-weight: 700; margin: 0; }}
    .metric-card {{
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 18px;
      background: linear-gradient(180deg, #ffffff 0%, #f4fbfb 100%);
    }}
    .metric-label {{ font-size: 13px; color: var(--muted); font-weight: 700; }}
    .metric-value {{ font-size: 42px; font-weight: 800; line-height: 1.1; margin-top: 8px; }}
    .metric-hint {{ color: var(--accent); font-weight: 700; margin: 6px 0 8px; }}
    ul {{ margin: 8px 0 0; padding-left: 22px; }}
    li {{ margin-bottom: 8px; }}
    .mail-block {{
      white-space: pre-wrap;
      font-family: "SFMono-Regular", Menlo, monospace;
      font-size: 13px;
      background: #0f172a;
      color: #dbeafe;
      border-radius: 18px;
      padding: 18px;
      overflow-wrap: anywhere;
    }}
    .strong {{
      border-left: 4px solid var(--accent);
      padding-left: 12px;
      margin-top: 12px;
      font-weight: 700;
    }}
    .price-list p {{ margin-bottom: 8px; }}
    @media (max-width: 820px) {{
      .hero-grid, .two-col {{ grid-template-columns: 1fr; }}
      .metric-value {{ font-size: 34px; }}
      .wrap {{ padding: 16px 12px 42px; }}
      .hero, .section {{ border-radius: 18px; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <p class="muted">{esc(timestamp_jst)} / signal_id {esc(result.get('signal_id', ''))}</p>
      <h1>{esc(subject)}</h1>
      <p>{esc(display_context.get('direction_label', ''))}。ただし今の扱いは「{display_context.get('action_label', '')}」で、方向とタイミングを分けて読む必要がある通知です。</p>
      <div>{chips_html(summary_chips)}</div>
      <div class="hero-grid">
        <div class="panel">
          <h2>最初に読む結論</h2>
          <p class="strong">相場の向き: {esc(display_context.get('direction_label', ''))}</p>
          <p class="strong">今の行動: {esc(display_context.get('action_label', ''))}</p>
          <p>今回の見どころは、「方向の強さ」と「実行しやすさ」が分離されている点です。方向が強くても、実際に入るにはまだ不利というケースを見分けやすくしています。</p>
        </div>
        <div class="panel">
          <h2>数字の読み方</h2>
          <p><strong>{esc(metric_labels['direction'])}</strong> は相場の向きの明確さです。</p>
          <p><strong>{esc(metric_labels['execution'])}</strong> は今この価格で仕掛ける条件の良さです。</p>
          <p><strong>{esc(metric_labels['wait'])}</strong> は待った方がよい圧力です。</p>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>主要ファクト</h2>
      <div class="fact-grid">{root_cards_html}</div>
    </section>

    <section class="section">
      <h2>3つの数字を丁寧に読む</h2>
      <div class="metric-grid">{''.join(metric_blocks)}</div>
    </section>

    <section class="section">
      <h2>価格帯と環境値</h2>
      <div class="two-col">
        <div class="panel price-list">
          <p><strong>現在価格:</strong> {esc(_format_price(result.get('current_price')))}</p>
          <p><strong>Funding:</strong> {esc(funding_display)}</p>
          <p><strong>ATR比 / 出来高比:</strong> {esc(result.get('atr_ratio'))} / {esc(result.get('volume_ratio'))}</p>
          <p><strong>近いサポート帯:</strong> {esc(_zone_summary('近いサポート帯', result.get('support_zones', []))).replace('近いサポート帯: ', '')}</p>
          <p><strong>近いレジスタンス帯:</strong> {esc(_zone_summary('近いレジスタンス帯', result.get('resistance_zones', []))).replace('近いレジスタンス帯: ', '')}</p>
        </div>
        <div class="panel">
          <h3>読み方の補足</h3>
          <ul>
            <li>近い価格帯は、次に試されやすい候補です。</li>
            <li>Funding は市場参加者の偏りの目安です。極端なら逆行リスクも増えます。</li>
            <li>ATR比と出来高比が高いと、勢いがある一方でノイズも増えやすくなります。</li>
          </ul>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>ロング / ショートの再検討ライン</h2>
      <div class="two-col">
        <div class="panel">
          <h3>ロング</h3>
          <p>{esc(_setup_line(result, 'long'))}</p>
        </div>
        <div class="panel">
          <h3>ショート</h3>
          <p>{esc(_setup_line(result, 'short'))}</p>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>待機理由または注意点</h2>
      <ul>{wait_reason_html}</ul>
    </section>

    <section class="section">
      <h2>AI補足の読み解き</h2>
      <div class="two-col">
        <div class="panel">
          <h3>補足判断</h3>
          <p>{esc(ai_reason or '補足判断はありません')}</p>
          <h3>次の確認条件</h3>
          <p>{esc(ai_next or '次条件の指定はありません')}</p>
        </div>
        <div class="panel">
          <h3>注意</h3>
          <ul>{ai_warning_html or '<li>追加の注意表示はありません</li>'}</ul>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>元メールの要点</h2>
      <div class="mail-block">{esc(raw_mail)}</div>
    </section>
  </div>
</body>
</html>
"""


def slugify_label(value: Any) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return "unknown"
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text or "unknown"


def detail_page_enabled(cfg: Any, result: dict[str, Any]) -> bool:
    if not bool(getattr(cfg, "NOTIFICATION_HTML_ENABLED", False)):
        return False
    if str(result.get("notification_kind", "main")).lower() == "attention":
        return bool(getattr(cfg, "NOTIFICATION_HTML_INCLUDE_ATTENTION", True))
    return True


def detail_page_paths(base_dir: Path, cfg: Any, result: dict[str, Any]) -> tuple[Path, str]:
    local_dir_raw = str(getattr(cfg, "NOTIFICATION_HTML_LOCAL_DIR", "logs/notifications_html")).strip() or "logs/notifications_html"
    local_root = Path(local_dir_raw)
    if not local_root.is_absolute():
        local_root = base_dir / local_root
    system_slug = slugify_label(result.get("system_label"))
    notification_kind = str(result.get("notification_kind", "main")).strip().lower() or "main"
    signal_id = str(result.get("signal_id", "")).strip() or datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    local_path = local_root / system_slug / notification_kind / f"{signal_id}.html"
    public_base = str(getattr(cfg, "NOTIFICATION_HTML_PUBLIC_BASE_URL", "https://server.afrog.jp/btc-monitor/notifications")).rstrip("/")
    public_url = f"{public_base}/{system_slug}/{notification_kind}/{signal_id}.html"
    return local_path, public_url


def publish_notification_detail(base_dir: Path, cfg: Any, result: dict[str, Any]) -> dict[str, Any]:
    local_path, public_url = detail_page_paths(base_dir, cfg, result)
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_text(build_notification_detail_html(result), encoding="utf-8")

    remote_host = str(getattr(cfg, "NOTIFICATION_HTML_REMOTE_SSH_HOST", "maruPro@macserver.afrog.jp")).strip()
    remote_root = str(getattr(cfg, "NOTIFICATION_HTML_REMOTE_DIR", "/Volumes/Server_HD2/site/btc-monitor/notifications")).strip()
    system_slug = slugify_label(result.get("system_label"))
    notification_kind = str(result.get("notification_kind", "main")).strip().lower() or "main"
    remote_dir = f"{remote_root.rstrip('/')}/{system_slug}/{notification_kind}"
    remote_path = f"{remote_dir}/{local_path.name}"

    subprocess.run(
        ["ssh", remote_host, "mkdir", "-p", remote_dir],
        check=True,
        capture_output=True,
        text=True,
        timeout=20,
    )
    subprocess.run(
        ["rsync", "-a", str(local_path), f"{remote_host}:{remote_path}"],
        check=True,
        capture_output=True,
        text=True,
        timeout=20,
    )
    return {
        "detail_page_enabled": True,
        "detail_page_status": "published",
        "detail_page_url": public_url,
        "detail_page_local_path": str(local_path),
        "detail_page_published_at_utc": datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def append_detail_page_url(body: str, url: str) -> str:
    if not str(url).strip():
        return body
    if str(url) in str(body):
        return body
    base = str(body).rstrip()
    return f"{base}\n\n【詳細ページ】\n{url}\n"
