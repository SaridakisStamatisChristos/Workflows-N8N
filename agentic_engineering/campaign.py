from __future__ import annotations

import argparse
import copy
import json
import re
import shutil
from pathlib import Path

from .contracts import ContractError
from .evidence import render_pr_body, write_evidence
from .io import load_jsonish
from .sandbox import execute_campaign


def _safe_branch_fragment(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-._")
    return (value or "task")[:48]


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute an engineering campaign and materialize only verified files")
    parser.add_argument("--source", required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--change-set", required=True)
    parser.add_argument("--policy", default=".agent/policy.yaml")
    parser.add_argument("--verification-config", default=".agent/verification.yaml")
    parser.add_argument("--sandbox-image")
    parser.add_argument("--mode", choices=["local", "docker"], default="docker")
    parser.add_argument("--artifact-dir", default="artifacts/agentic-campaign")
    parser.add_argument("--materialize-dir", default="artifacts/verified-tree")
    parser.add_argument("--apply-verified-to-source", action="store_true")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    task = load_jsonish(args.task)
    # Automatic campaign execution never trusts a model/task field to grant sensitive-path review.
    task.setdefault("authorization", {})
    task["authorization"]["human_review_granted"] = False
    change_set = load_jsonish(args.change_set)
    policy = load_jsonish(args.policy)
    if args.sandbox_image:
        # Runtime selection is controlled only by the trusted workflow invocation, never by issue/model text.
        policy = copy.deepcopy(policy)
        policy.setdefault("sandbox", {})["image"] = str(args.sandbox_image)
    verification = load_jsonish(args.verification_config)
    profile = task.get("verification_profile")
    commands = verification.get("profiles", {}).get(profile)
    if not isinstance(commands, list) or not commands:
        print(json.dumps({"ok": False, "error": f"unknown or empty trusted verification profile: {profile!r}"}))
        return 2

    temp_parent = None
    try:
        evidence, temp_parent = execute_campaign(
            source,
            task,
            change_set,
            policy,
            [str(x) for x in commands],
            mode=args.mode,
            keep_workspace=True,
        )
        if not evidence.get("measurement", {}).get("completed"):
            print(json.dumps({"ok": False, "error": "verification did not complete successfully"}))
            return 1

        artifact_dir = Path(args.artifact_dir)
        materialize_dir = Path(args.materialize_dir)
        artifact_dir.mkdir(parents=True, exist_ok=True)
        if materialize_dir.exists():
            shutil.rmtree(materialize_dir)
        materialize_dir.mkdir(parents=True, exist_ok=True)

        workspace = temp_parent / "workspace"
        deleted: list[str] = []
        for rel in evidence["files_changed"]:
            src = workspace / rel
            if src.exists():
                dst = materialize_dir / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
            else:
                deleted.append(rel)

        write_evidence(artifact_dir / "pr-evidence.json", evidence)
        (artifact_dir / "pr-body.md").write_text(render_pr_body(evidence), encoding="utf-8")
        metadata = {
            "task_id": task["task_id"],
            "branch_fragment": _safe_branch_fragment(task["task_id"]),
            "pr_title": "agent: " + re.sub(r"\s+", " ", str(task["title"])).strip()[:120],
            "base_ref": str(task.get("base_ref", "main")),
            "files_changed": evidence["files_changed"],
            "deleted_files": deleted,
            "verification_level": evidence["verification_level"],
        }
        (artifact_dir / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        if args.apply_verified_to_source:
            for rel in metadata["files_changed"]:
                src = workspace / rel
                dst = source / rel
                if src.exists():
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                elif dst.exists() and dst.is_file():
                    dst.unlink()

        print(json.dumps({"ok": True, "artifact_dir": str(artifact_dir), "materialize_dir": str(materialize_dir), "metadata": metadata}, sort_keys=True))
        return 0
    except (ContractError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 2
    finally:
        if temp_parent is not None:
            shutil.rmtree(temp_parent, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
