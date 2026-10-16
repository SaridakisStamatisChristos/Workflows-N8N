import json
import unittest
from pathlib import Path

from agentic_engineering.io import load_jsonish
from agentic_engineering.policy import classify_path

ROOT = Path(__file__).resolve().parents[1]

def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

class WorkflowContractTests(unittest.TestCase):
    def test_linear_intake_rehydrates_from_fixed_api_and_authenticates_relay(self):
        wf = load("workflows/engineering/70-linear-engineering-intake.json")
        webhook = next(n for n in wf["nodes"] if n["type"] == "n8n-nodes-base.webhook")
        self.assertEqual(webhook["parameters"].get("authentication"), "headerAuth")
        http = next(n for n in wf["nodes"] if n.get("name") == "Rehydrate From Linear API")
        self.assertEqual(http["parameters"].get("url"), "https://api.linear.app/graphql")
        policy_node = next(n for n in wf["nodes"] if n.get("name") == "Deterministic Eligibility Policy")
        self.assertIn("allowedProjects.size && !allowedProjects.has", policy_node["parameters"]["jsCode"])

    def test_change_generator_has_no_shell_or_write_adapter(self):
        wf = load("workflows/engineering/71-change-set-generator.json")
        types = {n["type"] for n in wf["nodes"]}
        self.assertNotIn("n8n-nodes-base.executeCommand", types)
        http = [n for n in wf["nodes"] if n["type"] == "n8n-nodes-base.httpRequest"]
        self.assertEqual(len(http), 1)
        self.assertEqual(http[0]["parameters"].get("url"), "https://api.openai.com/v1/responses")

    def test_campaign_dispatch_is_pinned_and_not_auto_retried(self):
        wf = load("workflows/engineering/72-agent-campaign-dispatch.json")
        http = next(n for n in wf["nodes"] if n["type"] == "n8n-nodes-base.httpRequest")
        self.assertEqual(http["parameters"].get("url"), "https://api.github.com/repos/SaridakisStamatisChristos/Workflows-N8N/actions/workflows/agentic-campaign-runner.yml/dispatches")
        self.assertFalse(http.get("retryOnFail", False))
        guard = next(n for n in wf["nodes"] if n.get("name") == "Deterministic Dispatch Guard")
        self.assertIn("payloadChars<=60000", guard["parameters"]["jsCode"])

    def test_runner_creates_draft_and_contains_no_merge_command(self):
        text = (ROOT / ".github/workflows/agentic-campaign-runner.yml").read_text(encoding="utf-8")
        self.assertIn("gh pr create", text)
        self.assertIn("--draft", text)
        self.assertNotIn("gh pr merge", text)
        self.assertNotIn("/merges", text)
        self.assertIn("--mode docker", text)

    def test_guardrail_implementation_is_self_protected(self):
        policy = load_jsonish(ROOT / ".agent/policy.yaml")
        task = {"allowed_paths": ["**"], "forbidden_paths": []}
        self.assertFalse(classify_path("agentic_engineering/sandbox.py", task, policy).allowed)
        self.assertFalse(classify_path("agentic_engineering/policy.py", task, policy).allowed)

if __name__ == "__main__":
    unittest.main()
