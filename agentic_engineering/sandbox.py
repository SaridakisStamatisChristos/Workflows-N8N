from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

from .contracts import ContractError, normalize_task, validate_change_set
from .evidence import changed_paths, snapshot, write_evidence
from .io import load_jsonish
from .policy import classify_issue, evaluate_paths


_ALLOWED_BOOTSTRAP_CAPABILITIES = {"CHOWN", "SETGID", "SETUID"}


def _safe_target(root: Path, rel: str) -> Path:
    rel = rel.replace('\\', '/')
    if rel.startswith('/') or '..' in Path(rel).parts:
        raise ContractError(f"unsafe path: {rel}")
    target = root / rel
    resolved_root = root.resolve()
    resolved_target = target.resolve(strict=False)
    try:
        resolved_target.relative_to(resolved_root)
    except ValueError as exc:
        raise ContractError(f"path escapes workspace: {rel}") from exc
    probe = root
    for part in Path(rel).parts[:-1]:
        probe = probe / part
        if probe.exists() and probe.is_symlink():
            raise ContractError(f"symlinked parent is not writable by agent: {rel}")
    if target.exists() and target.is_symlink():
        raise ContractError(f"symlink target is not writable by agent: {rel}")
    return target


def apply_change_set(workspace: Path, task: dict[str, Any], policy: dict[str, Any], change_set: dict[str, Any]) -> list[str]:
    max_bytes = int(policy.get("sandbox", {}).get("max_file_bytes", 1024 * 1024))
    planned = [str(op["path"]) for op in change_set["operations"]]
    decision = evaluate_paths(planned, task, policy)
    if not decision.allowed:
        raise ContractError("planned path policy denied change-set: " + "; ".join(decision.reasons))
    if decision.requires_human_review and not bool(task.get("authorization", {}).get("human_review_granted")):
        raise ContractError("planned change-set touches review-required paths without human authorization")

    for op in change_set["operations"]:
        target = _safe_target(workspace, op["path"])
        if op["op"] == "write_file":
            content = op["content"].encode("utf-8")
            if len(content) > max_bytes:
                raise ContractError(f"file exceeds max_file_bytes: {op['path']}")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        elif op["op"] == "delete_file":
            if target.exists():
                if not target.is_file():
                    raise ContractError(f"delete_file may only delete regular files: {op['path']}")
                target.unlink()
    return planned


def _sanitized_env(home: Path) -> dict[str, str]:
    return {
        "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "HOME": str(home),
        "PYTHONDONTWRITEBYTECODE": "1",
    }


def run_command_local(workspace: Path, command: str, timeout: int) -> dict[str, Any]:
    started = time.monotonic()
    try:
        proc = subprocess.run(
            ["bash", "-lc", command],
            cwd=workspace,
            env=_sanitized_env(workspace / ".home"),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
            check=False,
        )
        status = "passed" if proc.returncode == 0 else "failed"
        output = proc.stdout[-12000:]
        return {"command": command, "status": status, "exit_code": proc.returncode, "output": output, "duration_seconds": round(time.monotonic() - started, 3)}
    except subprocess.TimeoutExpired as exc:
        output = ((exc.stdout or "") + (exc.stderr or ""))[-12000:] if isinstance(exc.stdout, str) else ""
        return {"command": command, "status": "failed", "exit_code": 124, "output": output, "duration_seconds": round(time.monotonic() - started, 3), "failure": "timeout"}


def run_command_docker(workspace: Path, command: str, timeout: int, policy: dict[str, Any], image: str | None = None) -> dict[str, Any]:
    sandbox = policy.get("sandbox", {})
    image = image or str(sandbox.get("image", "python:3.12-slim@sha256:a6e34c598f2467ed0e9a8d349809fcd8b5c603269512df273a0bb1784edc11b1"))
    cap_add = [str(value).upper() for value in sandbox.get("cap_add", [])]
    unsupported = sorted(set(cap_add) - _ALLOWED_BOOTSTRAP_CAPABILITIES)
    if unsupported:
        raise ContractError("unsupported sandbox bootstrap capabilities: " + ", ".join(unsupported))
    args = [
        "docker", "run", "--rm",
        "--network", "none",
        "--cap-drop", "ALL",
    ]
    for capability in cap_add:
        args.extend(["--cap-add", capability])
    args.extend([
        "--security-opt", "no-new-privileges",
        "--pids-limit", str(sandbox.get("pids_limit", 128)),
        "--memory", str(sandbox.get("memory", "768m")),
        "--cpus", str(sandbox.get("cpus", "1.0")),
        "--read-only",
        "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m",
        "-v", f"{workspace.resolve()}:/workspace:rw",
        "-w", "/workspace",
        "-e", "PYTHONDONTWRITEBYTECODE=1",
        image,
        "sh", "-lc", command,
    ])
    started = time.monotonic()
    try:
        proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=timeout, check=False)
        return {
            "command": command,
            "status": "passed" if proc.returncode == 0 else "failed",
            "exit_code": proc.returncode,
            "output": proc.stdout[-12000:],
            "duration_seconds": round(time.monotonic() - started, 3),
            "sandbox": {"mode": "docker", "image": image, "network": "none", "bootstrap_capabilities": cap_add},
        }
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout[-12000:] if isinstance(exc.stdout, str) else ""
        return {"command": command, "status": "failed", "exit_code": 124, "output": output, "duration_seconds": round(time.monotonic() - started, 3), "failure": "timeout", "sandbox": {"mode": "docker", "image": image, "network": "none", "bootstrap_capabilities": cap_add}}


def execute_campaign(
    source: Path,
    task: dict[str, Any],
    change_set: dict[str, Any],
    policy: dict[str, Any],
    verification_commands: list[str],
    *,
    mode: str = "local",
    keep_workspace: bool = False,
) -> tuple[dict[str, Any], Path | None]:
    task = normalize_task(task)
    change_set = validate_change_set(change_set, task["task_id"])
    max_contract_chars = int(policy.get("sandbox", {}).get("max_change_set_chars", 60000))
    contract_chars = len(json.dumps(task, ensure_ascii=False)) + len(json.dumps(change_set, ensure_ascii=False)) + len(task["task_id"])
    if contract_chars > max_contract_chars:
        raise ContractError(f"combined task/change-set contract exceeds dispatch budget ({contract_chars}>{max_contract_chars})")
    issue_decision = classify_issue(task, policy)
    if not issue_decision.allowed:
        raise ContractError("task policy denied campaign: " + "; ".join(issue_decision.reasons))
    if issue_decision.requires_human_review and not bool(task.get("authorization", {}).get("human_review_granted")):
        raise ContractError("task requires human review before autonomous coding")

    temp_parent = Path(tempfile.mkdtemp(prefix="agentic-campaign-"))
    workspace = temp_parent / "workspace"
    shutil.copytree(source, workspace, symlinks=True, ignore=shutil.ignore_patterns('.git', 'artifacts'))
    before = snapshot(workspace)
    started = time.monotonic()
    tests: list[dict[str, Any]] = []
    known_failures: list[str] = []

    try:
        apply_change_set(workspace, task, policy, change_set)
        after_apply = snapshot(workspace)
        actual = changed_paths(before, after_apply)
        max_files = int(policy.get("sandbox", {}).get("max_files_changed", 40))
        if len(actual) > max_files:
            raise ContractError(f"actual changed file count {len(actual)} exceeds policy max {max_files}")
        actual_decision = evaluate_paths(actual, task, policy)
        if not actual_decision.allowed:
            raise ContractError("actual changed paths violate policy: " + "; ".join(actual_decision.reasons))
        if actual_decision.requires_human_review and not bool(task.get("authorization", {}).get("human_review_granted")):
            raise ContractError("actual changed paths require human review")

        max_runtime = int(policy.get("sandbox", {}).get("max_runtime_seconds", 900))
        for command in verification_commands:
            runner = run_command_docker if mode == "docker" else run_command_local
            result = runner(workspace, command, max_runtime, policy) if mode == "docker" else runner(workspace, command, max_runtime)
            tests.append(result)
            if result["status"] != "passed":
                known_failures.append(f"verification failed: {command}")
                break

        after_tests = snapshot(workspace)
        post_test_changes = changed_paths(after_apply, after_tests)
        if post_test_changes:
            known_failures.append("verification commands modified tracked workspace content: " + ", ".join(post_test_changes))

        success = bool(tests) and all(x["status"] == "passed" for x in tests) and not post_test_changes
        evidence = {
            "task": {
                "task_id": task["task_id"],
                "source": task["source"],
                "title": task["title"],
                "sensitivity": task.get("sensitivity", "normal"),
            },
            "repository": {"full_name": task["repository"], "base_ref": task.get("base_ref", "main")},
            "change_summary": [str(change_set.get("summary") or "Agent proposed a bounded change-set")],
            "files_changed": actual,
            "tests": tests,
            "static_checks": [
                {"name": "issue_policy", "status": "passed", "detail": issue_decision.as_dict()},
                {"name": "planned_path_policy", "status": "passed"},
                {"name": "actual_path_policy", "status": "passed", "detail": actual_decision.as_dict()},
            ] + ([{"name": "adversarial_model_review", "status": "passed", "detail": change_set.get("review_evidence")} ] if change_set.get("review_evidence") else []),
            "known_failures": known_failures,
            "risk_areas": list(actual_decision.reasons if actual_decision.requires_human_review else []),
            "sensitive_paths_touched": [p for p in actual if evaluate_paths([p], task, policy).requires_human_review],
            "assumptions": [
                "verification commands came from trusted repository benchmark/configuration, not issue text or model output",
                "model adversarial review is advisory evidence only and cannot authorize writes",
            ],
            "review_hotspots": actual,
            "agent_confidence": change_set.get("confidence"),
            "human_judgment_required": ["Review semantic correctness and scope before merging"] + (["Sensitive path review required"] if actual_decision.requires_human_review else []),
            "artifact_links": [],
            "measurement": {
                "completed": success,
                "wall_clock_seconds": round(time.monotonic() - started, 3),
                "retry_count": int(task.get("retry_count", 0)),
                "policy_violations": 0,
                "sandbox_mode": mode,
            },
            "verification_level": "RUNTIME_VERIFIED" if success else "STATICALLY_VERIFIED",
        }
        evidence_path = temp_parent / "pr-evidence.json"
        write_evidence(evidence_path, evidence)
        return evidence, (temp_parent if keep_workspace else None)
    finally:
        if not keep_workspace:
            shutil.rmtree(temp_parent, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a bounded agent change-set inside an isolated workspace")
    parser.add_argument("--source", required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--change-set", required=True)
    parser.add_argument("--policy", default=".agent/policy.yaml")
    parser.add_argument("--verification", action="append", default=[])
    parser.add_argument("--mode", choices=["local", "docker"], default="docker")
    parser.add_argument("--evidence-out", required=True)
    args = parser.parse_args()

    source = Path(args.source)
    task = load_jsonish(args.task)
    change_set = load_jsonish(args.change_set)
    policy = load_jsonish(args.policy)
    try:
        evidence, _ = execute_campaign(source, task, change_set, policy, args.verification, mode=args.mode)
    except (ContractError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 2
    write_evidence(Path(args.evidence_out), evidence)
    print(json.dumps({"ok": evidence["measurement"]["completed"], "evidence": args.evidence_out}))
    return 0 if evidence["measurement"]["completed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
