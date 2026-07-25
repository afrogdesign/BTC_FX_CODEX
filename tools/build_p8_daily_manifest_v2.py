from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.feedback.p8_daily_manifest_v2 import IdentityConflict, InputError, OutputConflict, build_manifest, read_csv, read_json, write_outputs

def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build independent P8 daily manifest v2 and P9 readiness v2 shadow")
    for name in ("cycle-manifest", "trial-report", "trial-facts", "review-queue", "cumulative-manifest", "modern-attribution-report", "output-root", "runtime-generation", "source-head", "cutoff-utc"): p.add_argument("--" + name, required=True)
    p.add_argument("--previous-v2-manifest"); p.add_argument("--claim-scope"); p.add_argument("--frozen-validation"); p.add_argument("--replace-output", action="store_true"); p.add_argument("--stdout-json", action="store_true")
    return p
def main(argv: list[str] | None = None) -> int:
    a = parser().parse_args(argv)
    try:
        cycle, _ = read_json(a.cycle_manifest, "cycle_manifest.json"); trial, _ = read_json(a.trial_report, "manual_operator_trial_evidence.json"); facts, _ = read_csv(a.trial_facts, "manual_operator_trial_facts.csv"); queue, _ = read_csv(a.review_queue, "manual_operator_trial_review_queue.csv"); cumulative, _ = read_json(a.cumulative_manifest, "evidence_manifest.json"); modern, _ = read_json(a.modern_attribution_report, "modern_attribution_report.json")
        previous = None
        if a.previous_v2_manifest: previous, _ = read_json(a.previous_v2_manifest, "previous_v2_manifest.json")
        scope = None
        if a.claim_scope:
            scope, _ = read_json(a.claim_scope, "claim_scope.json")
        validation = None
        if a.frozen_validation:
            validation, _ = read_json(a.frozen_validation, "frozen_validation.json")
        manifest, files = build_manifest(cycle, trial, facts, queue, cumulative, modern, a.runtime_generation, a.source_head, a.cutoff_utc, previous, scope, validation)
        write_outputs(a.output_root, files, a.replace_output)
        if a.stdout_json:
            q, actual = manifest["review_queue_delta"], manifest["actual_attribution_delta"]
            payload = {"ok": True, "run_id": manifest["run_id"], "report_date": manifest["report_date"], "operational_health": manifest["operational_health"]["state"], "comparison_status": manifest["generation_comparison"]["status"], "queue_new": len(q["new"]), "queue_backlog": len(q["backlog"]), "queue_resolved": len(q["resolved"]), "actual_new": len(actual["new"]), "actual_retained": len(actual["retained"]), "actual_lost": len(actual["lost"]), "readiness_v2_state": manifest["p9_readiness_v2"]["state"], "missing_requirements": manifest["p9_readiness_v2"]["missing_requirements"], "output_files": 4}
            sys.stdout.write(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
        return 0
    except IdentityConflict as exc:
        if a.stdout_json: sys.stdout.write(json.dumps({"ok": False, "error": str(exc)}, separators=(",", ":")) + "\n")
        return 3
    except OutputConflict as exc:
        if a.stdout_json: sys.stdout.write(json.dumps({"ok": False, "error": str(exc)}, separators=(",", ":")) + "\n")
        return 4
    except (InputError, ValueError, OSError) as exc:
        if a.stdout_json: sys.stdout.write(json.dumps({"ok": False, "error": str(exc)}, separators=(",", ":")) + "\n")
        return 2
if __name__ == "__main__": raise SystemExit(main())
