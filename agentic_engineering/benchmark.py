from __future__ import annotations

import argparse
import json
from pathlib import Path

from .contracts import ContractError
from .io import load_jsonish
from .sandbox import execute_campaign


ROOT = Path(__file__).resolve().parents[1]


def run_one(spec_path: Path, mode: str) -> dict:
    spec = load_jsonish(spec_path)
    task = spec["task"]
    policy = load_jsonish(ROOT / ".agent/policy.yaml")
    verification_cfg = load_jsonish(ROOT / ".agent/verification.yaml")
    commands = verification_cfg["profiles"][task["verification_profile"]]
    change_set = load_jsonish(ROOT / spec["fixture_change_set"])
    expected = spec.get("expected_outcome", "completed")
    observed = "unknown"
    evidence = None
    error = None
    try:
        evidence, _ = execute_campaign(
            ROOT / spec["fixture_source"],
            task,
            change_set,
            policy,
            commands,
            mode=mode,
        )
        observed = "completed" if evidence["measurement"]["completed"] else "verification_failed"
    except ContractError as exc:
        observed = "policy_rejected"
        error = str(exc)
    return {
        "benchmark_id": spec["id"],
        "classification": spec["classification"],
        "answer_material_present": bool(spec.get("answer_material_present")),
        "quality_claim_allowed": not bool(spec.get("answer_material_present")),
        "expected_outcome": expected,
        "observed_outcome": observed,
        "expectation_pass": observed == expected,
        "error": error,
        "evidence": evidence,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run reproducible agentic engineering benchmark fixtures")
    parser.add_argument("--mode", choices=["local", "docker"], default="local")
    parser.add_argument("--out", default="artifacts/benchmark-results.json")
    args = parser.parse_args()
    specs = sorted((ROOT / "benchmarks/tasks").glob("*.yaml"))
    results = [run_one(p, args.mode) for p in specs]
    payload = {
        "task_count": len(results),
        "expectation_pass_count": sum(r["expectation_pass"] for r in results),
        "expectation_pass_rate": (sum(r["expectation_pass"] for r in results) / len(results)) if results else None,
        "quality_benchmark_task_count": sum(r["quality_claim_allowed"] for r in results),
        "results": results,
        "claim_boundary": "Canned fixture change-sets validate pipeline and safety behavior only; they do not measure autonomous coding quality.",
    }
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: payload[k] for k in ("task_count", "expectation_pass_count", "expectation_pass_rate", "quality_benchmark_task_count")}, sort_keys=True))
    return 0 if payload["task_count"] and payload["expectation_pass_count"] == payload["task_count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
