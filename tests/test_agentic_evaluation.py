import unittest

from agentic_engineering.evaluate import summarize


class EvaluationTests(unittest.TestCase):
    def test_measured_manual_and_inferred_are_separate(self):
        result = {
            "measurement": {"completed": True, "wall_clock_seconds": 2.0, "retry_count": 1, "policy_violations": 0, "draft_pr_created": False},
            "tests": [{"status": "passed", "command": "x"}],
        }
        summary = summarize([result])
        self.assertEqual(summary["measured"]["tasks_attempted"], 1)
        self.assertEqual(summary["manual"]["reviewed_tasks"], 0)
        self.assertEqual(summary["inferred"], {})
        self.assertIsNone(summary["manual"]["reviewer_acceptance_rate"])


if __name__ == "__main__":
    unittest.main()
