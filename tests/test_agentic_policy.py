import unittest
from pathlib import Path

from agentic_engineering.contracts import ContractError, normalize_task, validate_change_set
from agentic_engineering.io import load_jsonish
from agentic_engineering.policy import classify_issue, classify_path, evaluate_paths


ROOT = Path(__file__).resolve().parents[1]
POLICY = load_jsonish(ROOT / ".agent/policy.yaml")
BASE_TASK = {
    "task_id": "T-1",
    "source": {"provider": "fixture", "source_id": "1", "provenance": "fixture"},
    "repository": "SaridakisStamatisChristos/Workflows-N8N",
    "title": "Small safe change",
    "description": "Update a normal source file",
    "labels": ["agent:auto"],
    "allowed_paths": ["src/**"],
    "forbidden_paths": ["src/forbidden/**"],
    "verification_profile": "fixture_python",
    "authorization": {"human_review_granted": False},
}


class PolicyTests(unittest.TestCase):
    def test_requires_explicit_auto_label(self):
        task = dict(BASE_TASK, labels=[])
        self.assertFalse(classify_issue(task, POLICY).allowed)

    def test_sensitive_issue_requires_review(self):
        task = dict(BASE_TASK, description="Change authentication behavior")
        result = classify_issue(task, POLICY)
        self.assertTrue(result.allowed)
        self.assertTrue(result.requires_human_review)

    def test_path_traversal_is_denied(self):
        result = classify_path("../host-secret", BASE_TASK, POLICY)
        self.assertFalse(result.allowed)

    def test_task_forbidden_path_is_denied(self):
        result = classify_path("src/forbidden/x.py", BASE_TASK, POLICY)
        self.assertFalse(result.allowed)

    def test_outside_allowlist_is_denied(self):
        result = classify_path("tests/test_x.py", BASE_TASK, POLICY)
        self.assertFalse(result.allowed)

    def test_guardrail_path_is_denied_even_if_task_claims_it(self):
        task = dict(BASE_TASK, allowed_paths=[".agent/**"])
        result = classify_path(".agent/policy.yaml", task, POLICY)
        self.assertFalse(result.allowed)

    def test_git_control_state_is_denied(self):
        task = dict(BASE_TASK, allowed_paths=["**"])
        self.assertFalse(classify_path(".git/config", task, POLICY).allowed)
        self.assertFalse(classify_path(".gitignore", task, POLICY).allowed)
        self.assertFalse(classify_path(".gitattributes", task, POLICY).allowed)

    def test_hidden_guardrail_path_remains_protected_under_global_allow(self):
        task = dict(BASE_TASK, allowed_paths=["**"])
        self.assertFalse(classify_path(".agent/policy.yaml", task, POLICY).allowed)

    def test_root_auth_path_is_denied(self):
        task = dict(BASE_TASK, allowed_paths=["**"])
        result = classify_path("auth/handler.py", task, POLICY)
        self.assertFalse(result.allowed)

    def test_change_set_task_id_must_match(self):
        with self.assertRaises(ContractError):
            validate_change_set({"task_id": "other", "operations": []}, "T-1")

    def test_normalize_rejects_bad_repository(self):
        task = dict(BASE_TASK, repository="not-a-repo")
        with self.assertRaises(ContractError):
            normalize_task(task)

    def test_evaluate_safe_paths(self):
        result = evaluate_paths(["src/a.py", "src/b.py"], BASE_TASK, POLICY)
        self.assertTrue(result.allowed)
        self.assertFalse(result.requires_human_review)


if __name__ == "__main__":
    unittest.main()
