import os
import unittest


class EnvironmentIsolationTests(unittest.TestCase):
    def test_common_provider_secrets_are_not_injected(self):
        for name in ("GITHUB_TOKEN", "OPENAI_API_KEY", "LINEAR_API_KEY", "N8N_ENCRYPTION_KEY"):
            self.assertNotIn(name, os.environ)


if __name__ == "__main__":
    unittest.main()
