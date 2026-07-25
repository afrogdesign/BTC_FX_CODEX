import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

class BundleCliTests(unittest.TestCase):
    def test_compact_success(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            headers = {"classifications":["classification_id","event_timestamp_utc","classifier_method_version"],"trial-facts":["trial_fact_id","event_timestamp_utc","classifier_method_version"],"episodes":["episode_id","opened_at_utc","association_method_version"],"links-v2":["link_id","episode_id","signal_id","entry_timestamp_jst","link_method_version","link_status","link_confidence","link_reason"],"signal-log":["signal_id","timestamp_utc","evaluation_trace_version"]}
            paths=[]
            for name, cols in headers.items():
                p=root/(name+".csv");
                with p.open("w", newline="", encoding="utf-8") as f:
                    w=csv.DictWriter(f, fieldnames=cols); w.writeheader()
                    values = {cols[0]: name+"1"}
                    values["event_timestamp_utc" if "event_timestamp_utc" in cols else ("opened_at_utc" if "opened_at_utc" in cols else ("entry_timestamp_jst" if "entry_timestamp_jst" in cols else "timestamp_utc"))] = "2026-07-24T00:00:00Z"
                    if name == "links-v2": values.update({"episode_id":"episodes1","signal_id":"signal-log1","link_status":"linked","link_confidence":"high","link_reason":"matched_unique_top_candidate"})
                    w.writerow(values)
                paths.append((name,p))
            args=[sys.executable,"tools/build_p_evidence_bundle.py"]
            for name,p in paths: args += ["--"+name,str(p)]
            args += ["--output-root",str(root/"out"),"--runtime-generation","r","--source-head","h","--cutoff-utc","2026-07-25T00:00:00Z","--stdout-json"]
            proc=subprocess.run(args, text=True, capture_output=True)
            self.assertEqual(proc.returncode,0,proc.stderr+proc.stdout); self.assertEqual(len(proc.stdout.splitlines()),1); self.assertEqual(json.loads(proc.stdout)["history_files"],8)

    def test_missing_input_is_compact_exit_two(self):
        proc = subprocess.run([sys.executable, "tools/build_p_evidence_bundle.py", "--classifications", "/missing", "--trial-facts", "/missing", "--episodes", "/missing", "--links-v2", "/missing", "--signal-log", "/missing", "--output-root", "/tmp/not-used", "--runtime-generation", "r", "--source-head", "h", "--cutoff-utc", "2026-07-25T00:00:00Z", "--stdout-json"], text=True, capture_output=True)
        self.assertEqual(proc.returncode, 2); self.assertNotIn("Traceback", proc.stdout + proc.stderr); self.assertEqual(len(proc.stdout.splitlines()), 1); self.assertNotIn("/missing", proc.stdout)

if __name__ == "__main__": unittest.main()
