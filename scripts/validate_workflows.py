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
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{20,}"),
]

WRITE_ADAPTER_PREFIXES = {"51", "52", "53", "54", "57", "58", "59"}
AUTONOMOUS_BANNED_TYPES = {"n8n-nodes-base.executeCommand"}

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

    for n in nodes:
        if not isinstance(n, dict):
            fail(path, "node entry must be an object")
            continue
        for required in ("name", "type", "typeVersion", "position", "parameters"):
            if required not in n:
                fail(path, f"node {n.get('name','<unnamed>')} missing {required}")

        if path.parts[-2] in {"autonomous", "actions"} and n.get("type") in AUTONOMOUS_BANNED_TYPES:
            fail(path, f"autonomous/action workflow uses banned node type {n.get('type')}")

        creds = n.get("credentials")
        if isinstance(creds, dict):
            for cred_type, spec in creds.items():
                if isinstance(spec, dict) and str(spec.get("id", "")).strip():
                    warnings.append(
                        f"{path.relative_to(ROOT)}: credential reference present for {cred_type}; "
                        "verify it is not instance-specific"
                    )

        if n.get("type") == "n8n-nodes-base.postgres":
            p = n.get("parameters", {})
            q = str(p.get("query", ""))
            if re.search(r"\$\d+", q):
                repl = p.get("options", {}).get("queryReplacement")
                if not repl:
                    fail(path, f"Postgres node {n.get('name')} uses $ parameters without queryReplacement")

    if path.parent.name == "actions" and path.name[:2] in WRITE_ADAPTER_PREFIXES:
        code = "\n".join(
            str(n.get("parameters", {}).get("jsCode", ""))
            for n in nodes if isinstance(n, dict)
        ).replace(" ", "")
        if "approved!==true" not in code:
            fail(path, "write adapter is missing explicit approved!==true guard")

    if path.parent.name == "operators":
        for n in nodes:
            if n.get("type") == "n8n-nodes-base.webhook":
                if n.get("parameters", {}).get("authentication") != "headerAuth":
                    fail(path, f"operator webhook {n.get('name')} must use headerAuth")

    if path.parent.name == "actions":
        for n in nodes:
            if n.get("type") == "n8n-nodes-base.httpRequest":
                url = str(n.get("parameters", {}).get("url", ""))
                if "=$json.url" in url or "={{ $json.url" in url:
                    fail(path, f"action HTTP node {n.get('name')} uses arbitrary user-controlled URL")

print(f"Validated {len(files)} workflow files")
for w in warnings:
    print(f"WARNING: {w}")
if errors:
    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
print("All workflow structural and safety checks passed")
