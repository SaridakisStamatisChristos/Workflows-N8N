from __future__ import annotations

from typing import Any


class ContractError(ValueError):
    pass


def normalize_task(raw: dict[str, Any]) -> dict[str, Any]:
    required = [
        "task_id",
        "source",
        "repository",
        "title",
        "description",
        "labels",
        "allowed_paths",
        "forbidden_paths",
        "verification_profile",
    ]
    missing = [key for key in required if key not in raw]
    if missing:
        raise ContractError(f"task missing required keys: {', '.join(missing)}")
    if not isinstance(raw["source"], dict):
        raise ContractError("task source must be an object")
    if not isinstance(raw["labels"], list):
        raise ContractError("task labels must be a list")
    if not isinstance(raw["allowed_paths"], list) or not isinstance(raw["forbidden_paths"], list):
        raise ContractError("allowed_paths and forbidden_paths must be lists")
    repository = str(raw["repository"])
    if repository.count("/") != 1 or repository.startswith("/") or repository.endswith("/"):
        raise ContractError("repository must be owner/name")

    task = dict(raw)
    task["task_id"] = str(raw["task_id"])
    task["repository"] = repository
    task["title"] = str(raw["title"])
    task["description"] = str(raw["description"])
    task["labels"] = [str(x) for x in raw["labels"]]
    task["allowed_paths"] = [str(x) for x in raw["allowed_paths"]]
    task["forbidden_paths"] = [str(x) for x in raw["forbidden_paths"]]
    task["verification_profile"] = str(raw["verification_profile"])
    task.setdefault("base_ref", "main")
    return task


def validate_change_set(raw: dict[str, Any], task_id: str, max_ops: int = 100) -> dict[str, Any]:
    if raw.get("task_id") != task_id:
        raise ContractError("change-set task_id does not match task")
    operations = raw.get("operations")
    if not isinstance(operations, list):
        raise ContractError("change-set operations must be a list")
    if len(operations) > max_ops:
        raise ContractError(f"change-set exceeds operation limit ({max_ops})")
    normalized = dict(raw)
    clean_ops: list[dict[str, Any]] = []
    for index, op in enumerate(operations):
        if not isinstance(op, dict):
            raise ContractError(f"operation {index} must be an object")
        kind = op.get("op")
        if kind not in {"write_file", "delete_file"}:
            raise ContractError(f"operation {index} has unsupported op {kind!r}")
        path = op.get("path")
        if not isinstance(path, str) or not path.strip():
            raise ContractError(f"operation {index} path must be non-empty string")
        item = {"op": kind, "path": path}
        if kind == "write_file":
            if not isinstance(op.get("content"), str):
                raise ContractError(f"operation {index} write_file requires string content")
            item["content"] = op["content"]
        clean_ops.append(item)
    normalized["operations"] = clean_ops
    confidence = raw.get("confidence")
    if confidence is not None:
        try:
            confidence = float(confidence)
        except Exception as exc:
            raise ContractError("confidence must be numeric") from exc
        if not 0.0 <= confidence <= 1.0:
            raise ContractError("confidence must be between 0 and 1")
        normalized["confidence"] = confidence
    return normalized
