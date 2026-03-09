from __future__ import annotations

import json
import smtplib
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any


def _pending_path(base_dir: Path) -> Path:
    return base_dir / "logs" / "errors" / "pending_email.json"


def send_email(
    *,
    smtp_host: str,
    smtp_port: int,
    smtp_user: str,
    smtp_password: str,
    mail_from: str,
    mail_to: str,
    subject: str,
    body: str,
) -> None:
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = mail_from
    msg["To"] = mail_to

    with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)


def save_pending_email(base_dir: Path, subject: str, body: str, retry_count: int = 0) -> None:
    path = _pending_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"subject": subject, "body": body, "retry_count": retry_count}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def resend_pending_email(base_dir: Path, cfg: Any) -> bool:
    path = _pending_path(base_dir)
    if not path.exists():
        return True
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        retry_count = int(payload.get("retry_count", 0))
        if retry_count >= 3:
            return False
        send_email(
            smtp_host=cfg.SMTP_HOST,
            smtp_port=cfg.SMTP_PORT,
            smtp_user=cfg.SMTP_USER,
            smtp_password=cfg.SMTP_PASSWORD,
            mail_from=cfg.MAIL_FROM,
            mail_to=cfg.MAIL_TO,
            subject=str(payload.get("subject", "")),
            body=str(payload.get("body", "")),
        )
        path.unlink(missing_ok=True)
        return True
    except Exception:  # noqa: BLE001
        payload = {"subject": "", "body": "", "retry_count": 1}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            pass
        payload["retry_count"] = int(payload.get("retry_count", 0)) + 1
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return False
