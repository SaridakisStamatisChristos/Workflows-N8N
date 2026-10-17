from __future__ import annotations

import argparse
import json
from pathlib import Path

from .evidence import write_evidence
from .io import load_jsonish
from .sandbox import execute_campaign


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the reproducible agentic engineering isolation check")
    parser.add_argument("--mode", choices=["local", "docker"], default="local")
    parser.add_argument("--out", default="artifacts/isolation-evidence.json")
    args = parser.parse_args()

    benchmark = load_jsonish(ROOT / "benchmarks/tasks/verified-change.yaml")
    task = benchmark["task"]
    change_set = load_jsonish(ROOT / benchmark["fixture_change_set"])
    policy = load_jsonish(ROOT / ".agent/policy.yaml")
    verification_config = load_jsonish(ROOT / ".agent/verification.yaml")
    commands = verification_config["profiles"][task["verification_profile"]]
    evidence, _ = execute_campaign(
        ROOT / benchmark["fixture_source"],
        task,
        change_set,
        policy,
        commands,
        mode=args.mode,
    )
    evidence["benchmark"] = {
        "id": benchmark["id"],
        "classification": benchmark["classification"],
        "answer_material_present": benchmark["answer_material_present"],
        "quality_claim_allowed": False,
    }
    out = ROOT / args.out
    write_evidence(out, evidence)
    print(json.dumps({"ok": evidence["measurement"]["completed"], "evidence": str(out), "classification": benchmark["classification"]}))
    return 0 if evidence["measurement"]["completed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
