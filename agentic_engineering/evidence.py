from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def snapshot(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
            continue
        rel = path.relative_to(root).as_posix()
        result[rel] = sha256_file(path)
    return result


def changed_paths(before: dict[str, str], after: dict[str, str]) -> list[str]:
    keys = set(before) | set(after)
    return sorted(path for path in keys if before.get(path) != after.get(path))


def render_pr_body(evidence: dict[str, Any]) -> str:
    tests = evidence.get("tests", [])
    test_lines = [f"- `{x.get('command','')}` — **{x.get('status','unknown')}**" for x in tests]
    changed = [f"- `{path}`" for path in evidence.get("files_changed", [])]
    failures = evidence.get("known_failures", [])
    failure_lines = [f"- {x}" for x in failures] or ["- None recorded"]
    judgement = evidence.get("human_judgment_required", [])
    judgement_lines = [f"- {x}" for x in judgement] or ["- Standard code review"]
    level = evidence.get("verification_level", "UNVERIFIED")
    return "\n".join(
        [
            "## Agent-generated draft PR evidence",
            "",
            f"**Verification level:** `{level}`",
            "",
            "### Changed files",
            *(changed or ["- No file changes recorded"]),
            "",
            "### Verification",
            *(test_lines or ["- No verification commands recorded"]),
            "",
            "### Known failures",
            *failure_lines,
            "",
            "### Human judgment required",
            *judgement_lines,
            "",
            "> This artifact contains conclusions and verification evidence, not private chain-of-thought.",
        ]
    )


def write_evidence(path: Path, evidence: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
