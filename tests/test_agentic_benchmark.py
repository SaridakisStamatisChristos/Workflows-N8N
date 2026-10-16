import unittest
from pathlib import Path

from agentic_engineering.benchmark import ROOT, run_one


class BenchmarkTests(unittest.TestCase):
    def test_all_fixture_expectations_hold_locally(self):
        for spec in sorted((ROOT / "benchmarks/tasks").glob("*.yaml")):
            with self.subTest(spec=spec.name):
                result = run_one(spec, "local")
                self.assertTrue(result["expectation_pass"], result)


if __name__ == "__main__":
    unittest.main()
