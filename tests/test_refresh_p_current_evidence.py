import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.refresh_p_current_evidence import _head, refresh


class RefreshCurrentEvidenceTests(unittest.TestCase):
    def test_incomplete_selected_directory_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); day = root / "logs/p8_operating_cycles/20260724"; day.mkdir(parents=True)
            (day / "cycle_manifest.json").write_text(json.dumps({"source": {"max_timestamp": "2026-07-24T00:00:00Z"}}))
            with self.assertRaisesRegex(ValueError, "selected_current_directory_incomplete"):
                refresh(root, root / "logs/p8_operating_cycles", root / "out", "Ver04-v5", "a" * 40)

    def test_source_head_override_is_recorded_and_invalid_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); day = root / "logs/p8_operating_cycles/20260724"; day.mkdir(parents=True)
            manifest = {"source": {"max_timestamp": "2026-07-24T00:00:00Z"}}
            (day / "cycle_manifest.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "invalid_source_head"):
                _head(root, "not-a-head")


if __name__ == "__main__":
    unittest.main()
