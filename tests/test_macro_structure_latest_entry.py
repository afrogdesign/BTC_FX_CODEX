from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.feedback import macro_structure_latest_entry as entry


ARTIFACT_ID = "operator_" + "a" * 20
SOURCE_DIGEST = "a" * 64
METADATA = {
    "as_of_utc": "2026-01-01T00:00:00+00:00",
    "as_of_jst": "2026-01-01T09:00:00+09:00",
    "evaluated_at_utc": "2026-01-01T01:00:00+00:00",
    "evaluated_at_jst": "2026-01-01T10:00:00+09:00",
    "stale_status": "current",
    "continuity_status": "continuous",
    "data_quality_status": "ok",
    "safety_boundary": "report-only / no automatic order / human decides manually",
}


def _source() -> str:
    return """<!doctype html><html><head><meta charset="utf-8"></head><body><section id="status"><h1>status</h1></section><section id="chart-4h"><h2>4H Macro Structure Chart</h2></section><section id="diagonal-evidence"><h2>Diagonal structure</h2></section><section id="structural-events"><h2>Structural events</h2></section><section id="scenario-hypotheses"><h2>Scenario hypotheses</h2></section><section id="zones"><h2>Reliable support/resistance evidence</h2></section><section id="chart"><h2>Supplemental 15m manual-confirmation view</h2></section><p>report-only / no automatic order / human decides manually</p></body></html>"""


def _source_dir(root: Path, text: str | None = None) -> Path:
    source_dir = root / ARTIFACT_ID
    source_dir.mkdir(parents=True)
    (source_dir / "macro_structure_operator.html").write_text(_source() if text is None else text, encoding="utf-8")
    (source_dir / "macro_structure_operator.json").write_text(json.dumps({"operator_artifact_id": ARTIFACT_ID}) + "\n", encoding="utf-8")
    return source_dir


class MacroStructureLatestEntryTests(unittest.TestCase):
    def test_entry_id_formulas_are_exact(self) -> None:
        available_expected = hashlib.sha256(f"{entry.METHOD_VERSION}|available|{ARTIFACT_ID}|{SOURCE_DIGEST}".encode()).hexdigest()[:20]
        unavailable_expected = hashlib.sha256(f"{entry.METHOD_VERSION}|unavailable|ohlcv_interval_invalid|{ARTIFACT_ID}|{SOURCE_DIGEST}".encode()).hexdigest()[:20]
        self.assertEqual(entry._entry_id_available(ARTIFACT_ID, SOURCE_DIGEST), available_expected)
        self.assertEqual(entry._entry_id_unavailable("ohlcv_interval_invalid", ARTIFACT_ID, SOURCE_DIGEST), unavailable_expected)

    def test_all_exact_section_ids_are_required(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source_dir = _source_dir(root)
            entry._source_bytes(source_dir, ARTIFACT_ID, SOURCE_DIGEST)
            for marker in entry.REQUIRED_SECTION_IDS:
                missing = _source().replace(marker, "", 1)
                broken = _source_dir(root / marker.replace('"', '').replace('=', '_'), missing)
                with self.assertRaisesRegex(ValueError, "latest_entry_source_incomplete"):
                    entry._source_bytes(broken, ARTIFACT_ID, SOURCE_DIGEST)

    def test_heading_without_required_section_id_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            text = _source().replace('id="scenario-hypotheses"', "", 1)
            source_dir = _source_dir(root, text)
            with self.assertRaisesRegex(ValueError, "latest_entry_source_incomplete"):
                entry._source_bytes(source_dir, ARTIFACT_ID, SOURCE_DIGEST)

    def test_each_prohibited_construct_is_rejected(self) -> None:
        prohibited = (
            "<script>alert(1)</script>", "<iframe src=\"#x\"></iframe>", "<object data=\"#x\"></object>",
            "<embed src=\"#x\">", "<meta http-equiv=\"refresh\" content=\"0\">", "fetch(\"x\")",
            "window.location=\"x\"", "location.href=\"x\"", "javascript:alert(1)",
            "<img src=\"https://example.invalid/a\">", "<a href=\"http://example.invalid\">x</a>",
            "<a href=\"//example.invalid\">x</a>",
        )
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for index, construct in enumerate(prohibited):
                source_dir = _source_dir(root / str(index), _source().replace("</body>", construct + "</body>", 1))
                with self.assertRaisesRegex(ValueError, "latest_entry_source_not_self_contained"):
                    entry._source_bytes(source_dir, ARTIFACT_ID, SOURCE_DIGEST)

    def test_available_bytes_are_deterministic_and_banner_is_immediately_after_body(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); source_dir = _source_dir(root); output = root / "output"
            first = entry.publish_available_entry(output_root=output, source_dir=source_dir, artifact_id=ARTIFACT_ID, source_digest=SOURCE_DIGEST, metadata=METADATA)
            first_bytes = (output / "latest.html").read_bytes()
            second = entry.publish_available_entry(output_root=output, source_dir=source_dir, artifact_id=ARTIFACT_ID, source_digest=SOURCE_DIGEST, metadata=METADATA)
            self.assertEqual(first["latest_entry_id"], second["latest_entry_id"])
            self.assertEqual(first_bytes, (output / "latest.html").read_bytes())
            text = first_bytes.decode("utf-8")
            self.assertTrue(text.startswith("<!doctype html><html><head><meta charset=\"utf-8\"></head><body><section id=\"fixed-latest-entry\""))

    def test_atomic_replace_failure_is_stable_and_cleans_temporary_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); source_dir = _source_dir(root); output = root / "output"; output.mkdir()
            target = output / "latest.html"; target.write_bytes(b"previous")
            with patch.object(entry.os, "replace", side_effect=OSError("platform path must not leak")):
                with self.assertRaises(entry.LatestEntryPublicationError):
                    entry.publish_available_entry(output_root=output, source_dir=source_dir, artifact_id=ARTIFACT_ID, source_digest=SOURCE_DIGEST, metadata=METADATA)
            self.assertEqual(target.read_bytes(), b"previous")
            self.assertEqual(list(output.glob(".latest-entry-*")), [])

    def test_unavailable_entry_formula_uses_previous_success_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); output = root / "output"; output.mkdir(); source_dir = _source_dir(output)
            (output / "latest.json").write_text(json.dumps({"operator_artifact_id": ARTIFACT_ID, "artifact_dir": ARTIFACT_ID, "source_digest": SOURCE_DIGEST, "as_of_utc": METADATA["as_of_utc"], "as_of_jst": METADATA["as_of_jst"]}), encoding="utf-8")
            result = entry.publish_unavailable_entry(output_root=output, error_code="ohlcv_interval_invalid")
            expected = entry._entry_id_unavailable("ohlcv_interval_invalid", ARTIFACT_ID, SOURCE_DIGEST)
            self.assertEqual(result["latest_entry_id"], expected)
            self.assertIn("error_code=ohlcv_interval_invalid", (output / "latest.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
