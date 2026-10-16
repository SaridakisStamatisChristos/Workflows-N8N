from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any, Iterable


@dataclass(frozen=True)
class Decision:
    allowed: bool
    requires_human_review: bool
    risk: str
    reasons: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "allowed": self.allowed,
            "requires_human_review": self.requires_human_review,
            "risk": self.risk,
            "reasons": list(self.reasons),
        }


def _norm_path(path: str) -> str:
    candidate = str(PurePosixPath(path.replace("\\", "/")))
    if candidate in {"", "."}:
        raise ValueError("path must not be empty")
    if candidate.startswith("/") or candidate == ".." or candidate.startswith("../") or "/../" in candidate:
        raise ValueError(f"path escapes repository: {path!r}")
    return candidate


def _matches(path: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def classify_issue(task: dict[str, Any], policy: dict[str, Any]) -> Decision:
    reasons: list[str] = []
    risk = "low"
    requires_review = False
    repository = str(task.get("repository", ""))
    allowlist = set(policy.get("repositories", {}).get("allowlist", []))
    if repository not in allowlist:
        return Decision(False, True, "critical", (f"repository is not allowlisted: {repository}",))
    labels = {str(x).strip().lower() for x in task.get("labels", [])}
    required_labels = {str(x).strip().lower() for x in policy.get("authorization", {}).get("auto_task_labels", [])}
    if required_labels and not labels.intersection(required_labels):
        return Decision(False, True, "high", ("task lacks an explicit autonomous-work authorization label",))
    text = "\n".join([str(task.get("title", "")), str(task.get("description", ""))] + [str(x) for x in task.get("labels", [])]).lower()
    blocked = [term for term in policy.get("sensitive_terms", {}).get("blocked", []) if str(term).lower() in text]
    if blocked:
        return Decision(False, True, "critical", tuple(f"blocked sensitive term: {x}" for x in blocked))
    review_terms = [term for term in policy.get("sensitive_terms", {}).get("review_required", []) if str(term).lower() in text]
    if review_terms:
        risk = "high"
        requires_review = True
        reasons.extend(f"sensitive term requires review: {x}" for x in review_terms)
    source = task.get("source", {}) or {}
    if source.get("provider") == "linear" and source.get("provenance") != "linear_api":
        requires_review = True
        risk = "high"
        reasons.append("Linear task was not re-hydrated from the Linear API")
    if not reasons:
        reasons.append("task passed deterministic issue eligibility policy")
    return Decision(True, requires_review, risk, tuple(reasons))


def classify_path(path: str, task: dict[str, Any], policy: dict[str, Any]) -> Decision:
    try:
        normalized = _norm_path(path)
    except ValueError as exc:
        return Decision(False, True, "critical", (str(exc),))
    reasons: list[str] = []
    risk = "low"
    review = False
    allowed_paths = [str(x) for x in task.get("allowed_paths", [])]
    forbidden_paths = [str(x) for x in task.get("forbidden_paths", [])]
    if allowed_paths and not _matches(normalized, allowed_paths):
        return Decision(False, True, "high", (f"path outside task allowlist: {normalized}",))
    if forbidden_paths and _matches(normalized, forbidden_paths):
        return Decision(False, True, "critical", (f"path matches task forbidden pattern: {normalized}",))
    for rule in policy.get("sensitive_paths", []):
        pattern = str(rule.get("pattern", ""))
        if pattern and fnmatch.fnmatchcase(normalized, pattern):
            action = rule.get("agent_write")
            rule_risk = str(rule.get("risk", "high"))
            reason = str(rule.get("reason", pattern))
            if action is False:
                return Decision(False, True, rule_risk, (f"protected path {normalized}: {reason}",))
            if action == "review_required":
                review = True
                risk = rule_risk
                reasons.append(f"sensitive path {normalized}: {reason}")
    if not reasons:
        reasons.append(f"path allowed by task and repository policy: {normalized}")
    return Decision(True, review, risk, tuple(reasons))


def evaluate_paths(paths: Iterable[str], task: dict[str, Any], policy: dict[str, Any]) -> Decision:
    aggregate: list[str] = []
    review = False
    risk = "low"
    order = {"low": 0, "moderate": 1, "high": 2, "critical": 3}
    for path in sorted(set(paths)):
        result = classify_path(path, task, policy)
        aggregate.extend(result.reasons)
        review = review or result.requires_human_review
        if order.get(result.risk, 2) > order.get(risk, 0):
            risk = result.risk
        if not result.allowed:
            return Decision(False, True, risk, tuple(aggregate))
    return Decision(True, review, risk, tuple(aggregate or ["no changed paths"]))
