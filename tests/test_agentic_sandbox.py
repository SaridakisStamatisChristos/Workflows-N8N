import tempfile
import unittest
from pathlib import Path

from agentic_engineering.contracts import ContractError
from agentic_engineering.evidence import snapshot
from agentic_engineering.io import load_jsonish
from agentic_engineering.sandbox import execute_campaign


ROOT = Path(__file__).resolve().parents[1]
POLICY = load_jsonish(ROOT / ".agent/policy.yaml")
BENCH = load_jsonish(ROOT / "benchmarks/tasks/pilot-simple-math.yaml")
CHANGE = load_jsonish(ROOT / BENCH["fixture_change_set"])
VERIFY = load_jsonish(ROOT / ".agent/verification.yaml")["profiles"]["fixture_python"]


class SandboxTests(unittest.TestCase):
    def test_local_pilot_produces_runtime_evidence(self):
        evidence, _ = execute_campaign(
            ROOT / BENCH["fixture_source"],
            BENCH["task"],
            CHANGE,
            POLICY,
            VERIFY,
            mode="local",
        )
        self.assertTrue(evidence["measurement"]["completed"])
        self.assertEqual(evidence["files_changed"], ["src/math_ops.py"])
        self.assertEqual(evidence["verification_level"], "RUNTIME_VERIFIED")

    def test_forbidden_test_mutation_is_rejected(self):
        bad = {
            "task_id": BENCH["task"]["task_id"],
            "operations": [{"op": "write_file", "path": "tests/test_math_ops.py", "content": "pass\n"}],
        }
        with self.assertRaises(ContractError):
            execute_campaign(
                ROOT / BENCH["fixture_source"],
                BENCH["task"],
                bad,
                POLICY,
                VERIFY,
                mode="local",
            )

    def test_oversized_dispatch_contract_is_rejected(self):
        task = dict(BENCH["task"])
        huge = {
            "task_id": task["task_id"],
            "operations": [{"op": "write_file", "path": "src/math_ops.py", "content": "x" * 61000}],
        }
        with self.assertRaises(ContractError):
            execute_campaign(ROOT / BENCH["fixture_source"], task, huge, POLICY, VERIFY, mode="local")

    def test_escape_mutation_is_rejected(self):
        bad = {
            "task_id": BENCH["task"]["task_id"],
            "operations": [{"op": "write_file", "path": "../escape.txt", "content": "x"}],
        }
        with self.assertRaises(ContractError):
            execute_campaign(
                ROOT / BENCH["fixture_source"],
                BENCH["task"],
                bad,
                POLICY,
                VERIFY,
                mode="local",
            )

    def test_dependency_caches_are_excluded_but_source_remains_evidenced(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            (root / "src/app.ts").write_text("export const value = 1;\n", encoding="utf-8")
            (root / "node_modules/pkg").mkdir(parents=True)
            (root / "node_modules/pkg/index.js").write_text("generated\n", encoding="utf-8")
            snap = snapshot(root)
            self.assertIn("src/app.ts", snap)
            self.assertNotIn("node_modules/pkg/index.js", snap)

    def test_sandbox_image_is_digest_pinned(self):
        image = POLICY["sandbox"]["image"]
        self.assertIn("@sha256:", image)


if __name__ == "__main__":
    unittest.main()
