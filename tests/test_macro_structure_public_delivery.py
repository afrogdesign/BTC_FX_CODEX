from __future__ import annotations

import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from src.notification.macro_structure_public_delivery import (
    DEFAULT_SOURCE_PATH,
    MacroPublicDeliveryError,
    format_macro_structure_email_block,
    publish_macro_structure_public,
    resolve_source_path,
    validate_fixed_entry_source,
)


def _cfg(source_path: str = DEFAULT_SOURCE_PATH, **overrides: object) -> SimpleNamespace:
    values = {
        "NOTIFICATION_HTML_ENABLED": True,
        "NOTIFICATION_HTML_PUBLIC_BASE_URL": "https://server.afrog.jp/btc-monitor/notifications",
        "NOTIFICATION_HTML_REMOTE_SSH_HOST": "maruPro@192.168.50.5",
        "NOTIFICATION_HTML_REMOTE_SSH_KEY": "~/.ssh/id_ed25519_afrog_lan",
        "NOTIFICATION_HTML_REMOTE_DIR": "/Volumes/Server_HD2/site/btc-monitor/notifications",
        "MACRO_STRUCTURE_FIXED_ENTRY_PATH": source_path,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def _available() -> str:
    return (
        '<!doctype html><html><body><section id="fixed-latest-entry">'
        "<b>entry ID</b>: entry_available_1234567890"
        "<b>entry_status</b>: available"
        "<b>entry method</b>: macro_structure_latest_entry.v1"
        "<b>source operator artifact ID</b>: operator_12345678901234567890"
        "<b>source digest</b>: " + "a" * 64 + ""
        "<b>source cutoff UTC</b>: 2026-07-21T20:00:00Z"
        "<b>source cutoff JST</b>: 2026-07-22T05:00:00+09:00"
        "<b>source stale status</b>: current"
        "<b>source continuity status</b>: continuous"
        "<b>source data-quality status</b>: ok"
        "fixed entry availability does not imply current market freshness; verify cutoff and status"
        "</section><section id=\"chart-4h\">4H Macro Structure Chart</section>"
        "<section id=\"structural-events\">Structural events</section>"
        "<section id=\"scenario-hypotheses\">Scenario hypotheses</section>"
        "<section id=\"chart\">Supplemental chart</section>"
        "report-only no automatic order human decides manually</body></html>"
    )


def _unavailable() -> str:
    return (
        '<!doctype html><html><body><section id="fixed-latest-entry-unavailable">'
        "<h1>Macro Structure Latest Entry Unavailable</h1>"
        "<b>entry ID</b>: entry_unavailable_1234567890"
        "entry_status=unavailable macro_structure_latest_entry.v1 "
        "no complete current entry was published for this attempt "
        "report-only no automatic order human decides manually"
        "</section></body></html>"
    )


def _write_source(root: Path, text: str, *, relative: str = DEFAULT_SOURCE_PATH) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class MacroStructurePublicDeliveryTests(unittest.TestCase):
    def test_default_source_path_resolves_under_base_dir(self) -> None:
        path = resolve_source_path(Path("/tmp/base"), _cfg())
        self.assertEqual(path, Path("/tmp/base") / DEFAULT_SOURCE_PATH)

    def test_available_source_is_normalized(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_source(Path(tmp), _available())
            model = validate_fixed_entry_source(path)
        self.assertEqual(model["entry_status"], "available")
        self.assertEqual(model["cutoff_jst"], "2026-07-22T05:00:00+09:00")
        self.assertEqual(model["source_sha256"], hashlib.sha256(_available().encode()).hexdigest())

    def test_unavailable_source_does_not_borrow_success_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            model = validate_fixed_entry_source(_write_source(Path(tmp), _unavailable()))
        self.assertEqual(model["entry_status"], "unavailable")
        self.assertEqual(model["source_artifact_id"], "")
        self.assertEqual(model["source_digest"], "")
        self.assertEqual(model["cutoff_jst"], "")

    def test_both_or_neither_state_fails_closed(self) -> None:
        for text in ("<body></body>", _available() + _unavailable()):
            with self.subTest(text=text[:20]):
                with tempfile.TemporaryDirectory() as tmp:
                    with self.assertRaises(MacroPublicDeliveryError) as caught:
                        validate_fixed_entry_source(_write_source(Path(tmp), text))
                self.assertEqual(caught.exception.code, "macro_public_source_invalid")

    def test_source_filesystem_and_safety_failures_are_stable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(MacroPublicDeliveryError, "macro_public_source_missing"):
                validate_fixed_entry_source(root / DEFAULT_SOURCE_PATH)
            path = _write_source(root, _available())
            path.unlink()
            path.symlink_to(root / "missing-target")
            with self.assertRaisesRegex(MacroPublicDeliveryError, "macro_public_source_unsafe"):
                validate_fixed_entry_source(path)
            path.unlink()
            path.write_bytes(b"\xff")
            with self.assertRaisesRegex(MacroPublicDeliveryError, "macro_public_source_invalid_utf8"):
                validate_fixed_entry_source(path)
            path.write_text("OPENAI_API_KEY=secret", encoding="utf-8")
            with self.assertRaisesRegex(MacroPublicDeliveryError, "macro_public_source_unsafe"):
                validate_fixed_entry_source(path)

    def test_oversized_source_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_source(Path(tmp), _available())
            with path.open("ab") as handle:
                handle.write(b"x" * (5 * 1024 * 1024))
            with self.assertRaisesRegex(MacroPublicDeliveryError, "macro_public_source_too_large"):
                validate_fixed_entry_source(path)

    def test_public_url_and_transport_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_source(root, _available())
            for key, value, code in (
                ("NOTIFICATION_HTML_PUBLIC_BASE_URL", "http://example.test", "macro_public_url_invalid"),
                ("NOTIFICATION_HTML_PUBLIC_BASE_URL", "//example.test", "macro_public_url_invalid"),
                ("NOTIFICATION_HTML_PUBLIC_BASE_URL", "https://user:pass@example.test", "macro_public_url_invalid"),
                ("NOTIFICATION_HTML_REMOTE_DIR", "relative/path", "macro_public_transport_config_invalid"),
                ("NOTIFICATION_HTML_REMOTE_DIR", "/safe/../unsafe", "macro_public_transport_config_invalid"),
                ("NOTIFICATION_HTML_REMOTE_SSH_HOST", "host\nunsafe", "macro_public_transport_config_invalid"),
            ):
                with self.subTest(key=key, value=value):
                    result = publish_macro_structure_public(root, _cfg(**{key: value}), runner=Mock())
                    self.assertEqual(result["macro_structure_public_status"], "failed")
                    self.assertEqual(result["macro_structure_public_error_code"], code)

    def test_disabled_does_not_read_or_run_transport(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runner = Mock()
            result = publish_macro_structure_public(Path(tmp), _cfg(NOTIFICATION_HTML_ENABLED=False), runner=runner)
        self.assertEqual(result["macro_structure_public_status"], "disabled")
        runner.assert_not_called()

    def test_publication_sequence_uses_arrays_and_unchanged_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = _write_source(root, _available())
            calls: list[tuple[list[str], dict[str, object]]] = []

            def runner(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
                calls.append((command, kwargs))
                return subprocess.CompletedProcess(command, 0, "", "")

            result = publish_macro_structure_public(root, _cfg(), runner=runner)
            self.assertEqual(result["macro_structure_public_status"], "published")
            self.assertEqual(result["macro_structure_public_url"], "https://server.afrog.jp/btc-monitor/notifications/macro-structure/latest.html")
            self.assertEqual(calls[0][0][0:2], ["ssh", "-o"])
            self.assertEqual(calls[0][0][-3:-1], ["mkdir", "-p"])
            self.assertEqual(calls[1][0][0], "rsync")
            self.assertEqual(calls[2][0][calls[2][0].index("mv")], "mv")
            self.assertTrue(all(kwargs.get("shell") is False for _, kwargs in calls))
            self.assertEqual(source.read_bytes(), _available().encode())
            self.assertNotIn("platform", result["macro_structure_public_error_code"])

    def test_publication_failure_has_stable_code_and_no_url(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_source(root, _available())
            runner = Mock(side_effect=OSError("raw ssh output must not leak"))
            result = publish_macro_structure_public(root, _cfg(), runner=runner)
        self.assertEqual(result["macro_structure_public_status"], "failed")
        self.assertEqual(result["macro_structure_public_error_code"], "macro_public_publish_failed")
        self.assertEqual(result["macro_structure_public_url"], "")

    def test_unavailable_source_is_published_with_fixed_url_but_no_success_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_source(root, _unavailable())
            result = publish_macro_structure_public(root, _cfg(), runner=Mock())
        self.assertEqual(result["macro_structure_public_status"], "published")
        self.assertEqual(result["macro_structure_public_entry_status"], "unavailable")
        self.assertEqual(result["macro_structure_public_url"], "https://server.afrog.jp/btc-monitor/notifications/macro-structure/latest.html")
        self.assertEqual(result["macro_structure_public_source_sha256"], hashlib.sha256(_unavailable().encode()).hexdigest())
        self.assertEqual(result["macro_structure_public_cutoff_jst"], "")

    def test_available_and_unavailable_email_blocks_are_bounded(self) -> None:
        available = {
            "macro_structure_public_status": "published",
            "macro_structure_public_url": "https://server.afrog.jp/btc-monitor/notifications/macro-structure/latest.html",
            "macro_structure_public_entry_status": "available",
            "macro_structure_public_cutoff_jst": "2026-07-22T05:00:00+09:00",
            "macro_structure_public_stale_status": "current",
            "macro_structure_public_continuity_status": "continuous",
            "macro_structure_public_data_quality_status": "ok",
        }
        block = format_macro_structure_email_block(available)
        self.assertEqual(block.count("https://"), 1)
        self.assertIn("cutoff JST=2026-07-22T05:00:00+09:00", block)
        self.assertIn("固定URLの存在は鮮度を保証しません", block)
        unavailable = dict(available, macro_structure_public_entry_status="unavailable")
        unavailable_block = format_macro_structure_email_block(unavailable)
        self.assertIn("状態: unavailable", unavailable_block)
        self.assertNotIn("cutoff JST", unavailable_block)
        failed = format_macro_structure_email_block({"macro_structure_public_status": "failed", "macro_structure_public_error_code": "macro_public_publish_failed"})
        self.assertEqual(failed, "【4H大局チャート】利用不可（macro_public_publish_failed）")
        self.assertNotIn("https://", failed)


if __name__ == "__main__":
    unittest.main()
