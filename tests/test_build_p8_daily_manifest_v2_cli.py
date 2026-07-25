import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

class P8CliTests(unittest.TestCase):
    def test_missing_input_exit_two_no_traceback(self):
        args=[sys.executable,"tools/build_p8_daily_manifest_v2.py"]
        for n in ("cycle-manifest","trial-report","trial-facts","review-queue","cumulative-manifest","modern-attribution-report"): args += ["--"+n,"/missing"]
        args += ["--output-root","/tmp/no","--runtime-generation","r","--source-head","0"*40,"--cutoff-utc","2026-07-25T00:00:00Z","--stdout-json"]
        p=subprocess.run(args,capture_output=True,text=True); self.assertEqual(p.returncode,2); self.assertNotIn("Traceback",p.stdout+p.stderr); self.assertEqual(len(p.stdout.splitlines()),1); self.assertNotIn("/missing",p.stdout)
    def test_success_has_four_files_and_one_line(self):
        root=Path("logs/p8_operating_cycles/20260724"); cumulative=Path("local/reports/p_evidence/wp3_wp4_acceptance_20260725/latest")
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/"out"; args=[sys.executable,"tools/build_p8_daily_manifest_v2.py","--cycle-manifest",str(root/"cycle_manifest.json"),"--trial-report",str(root/"manual_operator_trial_evidence.json"),"--trial-facts",str(root/"manual_operator_trial_facts.csv"),"--review-queue",str(root/"manual_operator_trial_review_queue.csv"),"--cumulative-manifest",str(cumulative/"evidence_manifest.json"),"--modern-attribution-report",str(cumulative/"modern_attribution_report.json"),"--output-root",str(out),"--runtime-generation","Ver04-v5","--source-head","0"*40,"--cutoff-utc","2026-07-25T01:05:00.785295Z","--stdout-json"]
            p=subprocess.run(args,capture_output=True,text=True); self.assertEqual(p.returncode,0,p.stdout+p.stderr); self.assertEqual(len(p.stdout.splitlines()),1); self.assertEqual(json.loads(p.stdout)["output_files"],4); self.assertEqual(len(list(out.iterdir())),4)

if __name__ == "__main__": unittest.main()
