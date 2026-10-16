# Validation and Runtime Testing

## Repository CI

Run:

```bash
python scripts/validate_workflows.py
python scripts/test_contracts.py
```

The structural validator checks:

- JSON parsing and required n8n node fields;
- connection sources/targets;
- common hardcoded-secret patterns;
- approval guards on concrete write adapters;
- Header Auth on generic operator webhooks;
- positional parameters on Postgres SQL;
- arbitrary user-controlled HTTP URLs in action workflows;
- banned shell execution in autonomous/action layers.

The contract suite checks:

- command center and dispatcher support the same action vocabulary;
- approval Wait uses Header Auth;
- completion uses the originally claimed idempotency key;
- GitHub write endpoints are pinned to `api.github.com/repos`;
- Slack uses the native Slack Trigger;
- Discord relay uses Header Auth;
- Postgres backends preserve the portable workflow input contracts;
- scheduled daily autonomy remains read-only.

## Runtime smoke matrix

Repository CI cannot substitute for a live n8n instance. Before production, verify:

1. read-only request -> HTTP 200 -> result persisted;
2. high-risk read-only request -> HTTP 202 -> rejection path stores decision;
3. `gmail_send` -> 202 -> approve -> exactly one email;
4. repeat same request ID/action -> duplicate suppressed;
5. Slack allowlisted mention -> command-center response returned to same channel;
6. non-allowlisted Slack user/channel -> ignored;
7. Discord verified relay + allowlisted principal -> native Discord reply;
8. untrusted Discord relay call -> HTTP 403;
9. GitHub issue creation with write token -> exactly one issue;
10. GitHub file update with stale SHA -> GitHub rejects instead of overwriting;
11. Postgres ledger concurrent duplicate claims -> exactly one winner;
12. health endpoint returns 503 when a checked provider credential/path is broken;
13. metrics endpoint surfaces a deliberately created stale claim.

## Failure injection

Test ambiguous provider failures separately. Do not reset a claimed idempotency key until the external provider outcome has been checked.
