#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / "workflows"
errors = []
warnings = []
secret_patterns = [
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
]

def fail(path, msg):
    errors.append(f"{path.relative_to(ROOT)}: {msg}")

def walk_targets(value):
    if isinstance(value, dict):
        if isinstance(value.get("node"), str):
            yield value["node"]
        for v in value.values():
            yield from walk_targets(v)
    elif isinstance(value, list):
        for v in value:
            yield from walk_targets(v)

files = sorted(WORKFLOWS.rglob("*.json"))
if not files:
    errors.append("No workflow JSON files found")

for path in files:
    text = path.read_text(encoding="utf-8")
    for pattern in secret_patterns:
        if pattern.search(text):
            fail(path, f"possible hardcoded secret matching {pattern.pattern}")
    try:
        data = json.loads(text)
    except Exception as exc:
        fail(path, f"invalid JSON: {exc}")
        continue
    if not isinstance(data, dict):
        fail(path, "top-level JSON must be an object")
        continue
    if not isinstance(data.get("name"), str) or not data["name"].strip():
        fail(path, "missing workflow name")
    nodes = data.get("nodes")
    connections = data.get("connections")
    if not isinstance(nodes, list) or not nodes:
        fail(path, "nodes must be a non-empty list")
        continue
    if not isinstance(connections, dict):
        fail(path, "connections must be an object")
        continue
    names = [n.get("name") for n in nodes if isinstance(n, dict)]
    if len(names) != len(set(names)):
        fail(path, "node names must be unique")
    node_names = set(n for n in names if isinstance(n, str))
    for source, graph in connections.items():
        if source not in node_names:
            fail(path, f"connection source does not exist: {source}")
        for target in walk_targets(graph):
            if target not in node_names:
                fail(path, f"connection target does not exist: {target}")
    for node in nodes:
        if not isinstance(node, dict):
            fail(path, "node entry must be an object")
            continue
        for required in ("name", "type", "typeVersion", "position", "parameters"):
            if required not in node:
                fail(path, f"node {node.get('name','<unnamed>')} missing {required}")
        creds = node.get("credentials")
        if isinstance(creds, dict):
            for cred_type, spec in creds.items():
                if isinstance(spec, dict) and str(spec.get("id", "")).strip():
                    warnings.append(f"{path.relative_to(ROOT)}: credential reference present for {cred_type}; verify it is not instance-specific")
    if path.parent.name == "actions" and path.name[:2] in {"51","52","53","54"}:
        code = "\n".join(
            str(n.get("parameters", {}).get("jsCode", ""))
            for n in nodes if isinstance(n, dict)
        )
        if "approved!==true" not in code.replace(" ", ""):
            fail(path, "write adapter is missing explicit approved!==true guard")

print(f"Validated {len(files)} workflow files")
for w in warnings:
    print(f"WARNING: {w}")
if errors:
    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
print("All workflow structural checks passed")
