from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.feedback.p8_daily_manifest_v2 import IdentityConflict, InputError, OutputConflict, QUEUE_HEADERS, TRIAL_HEADERS, build_manifest, read_csv, read_json, write_outputs

def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build independent P8 daily manifest v2 and P9 readiness v2 shadow")
    for name in ("cycle-manifest", "trial-report", "trial-facts", "review-queue", "cumulative-manifest", "modern-attribution-report", "output-root", "runtime-generation"): p.add_argument("--" + name, required=True)
    p.add_argument("--source-head")
    p.add_argument("--cutoff-utc")
    p.add_argument("--previous-v2-manifest"); p.add_argument("--claim-scope"); p.add_argument("--frozen-validation"); p.add_argument("--replace-output", action="store_true"); p.add_argument("--stdout-json", action="store_true")
    return p
def main(argv: list[str] | None = None) -> int:
    a = parser().parse_args(argv)
    try:
        cycle, cycle_meta = read_json(a.cycle_manifest, "cycle_manifest"); trial, trial_meta = read_json(a.trial_report, "trial_report"); facts, facts_meta = read_csv(a.trial_facts, "trial_facts", TRIAL_HEADERS); queue, queue_meta = read_csv(a.review_queue, "review_queue", QUEUE_HEADERS); cumulative, cumulative_meta = read_json(a.cumulative_manifest, "cumulative_manifest"); modern, modern_meta = read_json(a.modern_attribution_report, "modern_attribution_report")
        root = Path(__file__).resolve().parents[1]
        source_head = a.source_head
        explicit_source = bool(source_head)
        if not source_head:
            source_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        if not source_head or not re.fullmatch(r"[0-9a-fA-F]{40}", source_head): raise InputError("invalid_source_head")
        cutoff = a.cutoff_utc or cycle.get("source", {}).get("max_timestamp")
        if not cutoff: raise InputError("missing_cutoff_utc")
        cumulative["_input_fingerprint"] = cumulative_meta["fingerprint"]; modern["_input_fingerprint"] = modern_meta["fingerprint"]
        previous = None
        if a.previous_v2_manifest: previous, _ = read_json(a.previous_v2_manifest, "previous_v2_manifest.json")
        scope = None
        if a.claim_scope:
            scope, _ = read_json(a.claim_scope, "claim_scope.json")
        validation = None
        if a.frozen_validation:
            validation, _ = read_json(a.frozen_validation, "frozen_validation.json")
        input_meta = {"cycle_manifest": cycle_meta, "trial_report": trial_meta, "trial_facts": facts_meta, "review_queue": queue_meta, "cumulative_manifest": cumulative_meta, "modern_attribution_report": modern_meta}
        manifest, files = build_manifest(cycle, trial, facts, queue, cumulative, modern, a.runtime_generation, source_head, cutoff, previous, scope, validation, input_meta)
        manifest["source_head_resolution"] = "explicit_override" if explicit_source else "git"
        files["p8_daily_manifest_v2.json"] = (json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()
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
    except (InputError, ValueError) as exc:
        if a.stdout_json: sys.stdout.write(json.dumps({"ok": False, "error": str(exc)}, separators=(",", ":")) + "\n")
        return 2
    except OSError as exc:
        if a.stdout_json: sys.stdout.write(json.dumps({"ok": False, "error": "output_transaction_conflict"}, separators=(",", ":")) + "\n")
        return 4
if __name__ == "__main__": raise SystemExit(main())
