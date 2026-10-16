from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_jsonish(path: str | Path) -> Any:
    """Load repository-owned JSON or JSON-compatible YAML without third-party deps."""
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8"))


def dump_json(path: str | Path, value: Any) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
