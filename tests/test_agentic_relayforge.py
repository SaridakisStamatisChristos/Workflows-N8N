import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELAYFORGE = "SaridakisStamatisChristos/RelayForge"


class RelayForgeTargetTests(unittest.TestCase):
    def test_relayforge_is_explicitly_allowlisted(self):
        policy = json.loads((ROOT / ".agent/policy.yaml").read_text(encoding="utf-8"))
        self.assertIn(RELAYFORGE, policy["repositories"]["allowlist"])
        self.assertFalse(policy["authorization"]["allow_merge"])
        self.assertEqual(policy["authorization"]["publish_mode"], "draft_pr_only")

    def test_runner_uses_separate_target_checkout_and_scoped_secret(self):
        text = (ROOT / ".github/workflows/agentic-campaign-runner.yml").read_text(encoding="utf-8")
        self.assertIn("repository: ${{ steps.contract.outputs.repository }}", text)
        self.assertIn("path: target", text)
        self.assertIn("RELAYFORGE_GITHUB_TOKEN", text)
        self.assertIn("--source \"$GITHUB_WORKSPACE/target\"", text)
        self.assertIn("--sandbox-image relayforge-verifier:node22-pnpm10", text)
        self.assertIn("$GITHUB_WORKSPACE/target/.agent/verification.yaml", text)
        self.assertIn("--draft", text)
        self.assertNotIn("gh pr merge", text)
        self.assertNotIn("/merges", text)

    def test_runner_rejects_unallowlisted_repository_before_checkout(self):
        text = (ROOT / ".github/workflows/agentic-campaign-runner.yml").read_text(encoding="utf-8")
        guard = "if repository not in allowlist:"
        checkout = "name: Checkout authorized target repository"
        self.assertIn(guard, text)
        self.assertIn(checkout, text)
        self.assertLess(text.index(guard), text.index(checkout))

    def test_relayforge_verifier_has_pinned_pnpm_and_local_postgres(self):
        dockerfile = (ROOT / "docker/relayforge-verifier.Dockerfile").read_text(encoding="utf-8")
        entrypoint = (ROOT / "scripts/relayforge-verifier-entrypoint.sh").read_text(encoding="utf-8")
        self.assertIn("PNPM_VERSION=10.18.3", dockerfile)
        self.assertIn("postgresql", dockerfile)
        self.assertIn("npm install --global", dockerfile)
        self.assertIn("/tmp/pgsocket", entrypoint)
        self.assertIn("DATABASE_URL", entrypoint)
        self.assertNotIn("curl ", entrypoint)
        self.assertNotIn("wget ", entrypoint)

    def test_ci_smokes_verifier_with_network_disabled(self):
        text = (ROOT / ".github/workflows/agentic-engineering-ci.yml").read_text(encoding="utf-8")
        self.assertIn("docker/relayforge-verifier.Dockerfile", text)
        self.assertIn("--network none", text)
        self.assertIn("pg_isready", text)

    def test_sandbox_image_can_only_be_selected_by_campaign_cli(self):
        campaign = (ROOT / "agentic_engineering/campaign.py").read_text(encoding="utf-8")
        self.assertIn('parser.add_argument("--sandbox-image")', campaign)
        self.assertIn('policy.setdefault("sandbox", {})["image"]', campaign)
        self.assertNotIn('task.get("sandbox_image")', campaign)
        self.assertNotIn('change_set.get("sandbox_image")', campaign)


if __name__ == "__main__":
    unittest.main()
