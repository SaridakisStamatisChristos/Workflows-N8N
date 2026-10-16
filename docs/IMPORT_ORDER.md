# Import and Wiring Order

1. Import `05-memory-store.json`.
2. Import `10-research-specialist.json`.
3. Import `20-engineering-specialist.json`.
4. Import `30-communications-specialist.json`.
5. Import `35-github-readonly-specialist.json`.
6. Import `90-error-handler.json` and select it as the error workflow for the command center/specialists if desired.
7. Import `00-autonomous-command-center.json` last.

## Bind sub-workflow IDs

Open each Execute Sub-workflow node in the command center and select the imported workflow that matches its label. The portable export contains `REPLACE_*_WORKFLOW_ID` placeholders because n8n assigns workflow IDs at import time.

## Credentials

- **Command Webhook**: Header Auth credential.
- **OpenAI Router / specialist OpenAI nodes**: HTTP Bearer Auth credential containing the OpenAI API key.
- **GitHub specialist HTTP nodes**: HTTP Bearer Auth credential containing a GitHub token with read-only access to the repositories you intend to inspect.
- **Wait for Human Approval**: configure incoming Header Auth if your n8n build requires/selects it separately.

## Publish order

Test each specialist independently first. Then activate/publish the memory and specialists required by your n8n version. Finally test and publish the command center.

## Smoke test

POST to the command webhook with:

```json
{
  "task": "Research the current state of durable workflow orchestration and identify three design risks.",
  "priority": "normal",
  "context": {"goal": "production automation"}
}
```

Expected: route `research`, structured specialist output, and either HTTP 200 or HTTP 202 if policy marks the request high-risk.
