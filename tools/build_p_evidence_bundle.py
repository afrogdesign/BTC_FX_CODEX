from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.contracts.generation_identity import GenerationIdentity
from src.feedback.p_cumulative_evidence import EvidenceIdentityConflict, EvidenceInputError, EvidenceOutputConflict, build_bundle, read_logical_csv, write_bundle

def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the report-only cumulative P evidence bundle")
    for name in ("classifications", "trial-facts", "episodes", "links-v2", "signal-log", "output-root", "runtime-generation", "source-head", "cutoff-utc"):
        parser.add_argument("--" + name, required=True)
    for name in ("exact-observations", "active-plan-candidates", "signal-outcomes"):
        parser.add_argument("--" + name)
    parser.add_argument("--stdout-json", action="store_true")
    return parser

def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        generation = GenerationIdentity(program="P", runtime_generation=args.runtime_generation, source_head=args.source_head, schema_version="p_cumulative_evidence.v1", method_version="p_cumulative_evidence.v1", cutoff_utc=args.cutoff_utc, classifier_version="manual_operator_classifier.v4", linker_version="manual_trade_signal_link.v2", p8_evidence_version="manual_operator_trial_evidence.v1")
        paths = {"classifications": args.classifications, "trial_facts": args.trial_facts, "episodes": args.episodes, "links_v2": args.links_v2, "signal_log": args.signal_log, "exact_observations": args.exact_observations, "active_plan_candidates": args.active_plan_candidates, "signal_outcomes": args.signal_outcomes}
        inputs = {}
        for name, path in paths.items():
            if path: inputs[name] = read_logical_csv(path, name + ".csv")
        files, result = build_bundle(inputs, generation, args.cutoff_utc)
        write_bundle(args.output_root, files, result["run_id"])
        if args.stdout_json:
            payload = {"ok": True, "run_id": result["run_id"], "baseline_episodes": result["modern"]["report"]["baseline_episodes"], "baseline_links": result["modern"]["report"]["baseline_links"], "evidence_facts": len(result["manifest"].get("cohort_counts", {})) and sum(result["manifest"].get("cohort_counts", {}).values()), "review_queue": len(result["modern"]["queue"]), "automatic_causal_claims": 0, "canonical_link_replacement": False, "history_files": 8, "latest_files": 8}
            sys.stdout.write(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
        return 0
    except (EvidenceInputError, ValueError) as exc:
        if args.stdout_json: sys.stdout.write(json.dumps({"ok": False, "error": str(exc)}, sort_keys=True, separators=(",", ":")) + "\n")
        return 3 if "conflict" in str(exc) else 2
    except (EvidenceOutputConflict, OSError) as exc:
        if args.stdout_json: sys.stdout.write(json.dumps({"ok": False, "error": str(exc)}, sort_keys=True, separators=(",", ":")) + "\n")
        return 4

if __name__ == "__main__":
    raise SystemExit(main())
