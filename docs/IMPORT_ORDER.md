# Import and Wiring Order

## 1. Choose persistence

Portable single-instance default:

1. `workflows/autonomous/05-memory-store.json`
2. `workflows/actions/55-action-ledger.json`

Durable Postgres alternative:

1. `workflows/storage/06-postgres-memory-store.json`
2. `workflows/storage/56-postgres-action-ledger.json`

Both variants preserve the same sub-workflow input contracts. Bind Postgres credentials on every Postgres node if you choose the durable backend.

## 2. Import read-only specialists

3. `workflows/autonomous/10-research-specialist.json`
4. `workflows/autonomous/20-engineering-specialist.json`
5. `workflows/autonomous/30-communications-specialist.json`
6. `workflows/autonomous/35-github-readonly-specialist.json`
7. `workflows/autonomous/90-error-handler.json`
8. `workflows/autonomous/91-recovery-advisor.json`

## 3. Import write adapters

9. `workflows/actions/51-gmail-send-approved.json`
10. `workflows/actions/52-calendar-create-approved.json`
11. `workflows/actions/53-drive-create-text-approved.json`
12. `workflows/actions/54-telegram-notify-approved.json`
13. `workflows/actions/57-github-write-approved.json`
14. `workflows/actions/58-slack-notify-approved.json`
15. `workflows/actions/59-discord-notify-approved.json`
16. `workflows/actions/50-approved-action-dispatcher.json`

Bind the dispatcher placeholders:

- `REPLACE_GMAIL_ACTION_WORKFLOW_ID`
- `REPLACE_CALENDAR_ACTION_WORKFLOW_ID`
- `REPLACE_DRIVE_ACTION_WORKFLOW_ID`
- `REPLACE_TELEGRAM_ACTION_WORKFLOW_ID`
- `REPLACE_SLACK_ACTION_WORKFLOW_ID`
- `REPLACE_DISCORD_ACTION_WORKFLOW_ID`
- `REPLACE_GITHUB_WRITE_ACTION_WORKFLOW_ID`
- `REPLACE_ACTION_LEDGER_WORKFLOW_ID`

The ledger claim is deliberately conservative. If a provider call fails ambiguously after the claim, the key remains claimed until an operator investigates and explicitly resets it. This prevents accidental duplicate side effects.

## 4. Import command center

17. `workflows/autonomous/00-autonomous-command-center.json`

Bind:

- `REPLACE_MEMORY_WORKFLOW_ID`
- `REPLACE_RESEARCH_WORKFLOW_ID`
- `REPLACE_ENGINEERING_WORKFLOW_ID`
- `REPLACE_COMMUNICATIONS_WORKFLOW_ID`
- `REPLACE_GITHUB_WORKFLOW_ID`
- `REPLACE_ACTION_DISPATCHER_WORKFLOW_ID`

Assign Header Auth separately to:

- `Command Webhook`;
- `Wait for Human Approval`.

They are separate inbound trust boundaries.

## 5. Assign credentials

- OpenAI router/specialists/health: HTTP Bearer Auth containing the OpenAI API key.
- GitHub read-only specialist: least-privilege GitHub read token.
- GitHub approved write adapter: separate least-privilege GitHub write token.
- Gmail action: Gmail OAuth2.
- Calendar action: Google Calendar OAuth2.
- Drive action: Google Drive OAuth2.
- Telegram workflows: Telegram bot credential.
- Slack workflows: Slack credential with signing secret configured for the trigger.
- Discord workflows: Discord bot credential.
- Postgres backend/metrics: Postgres credential.

Do not put static secrets in Code nodes, Set nodes, request headers, or committed JSON.

## 6. Import operator gateways

18. `workflows/operators/60-telegram-command-gateway.json`
19. `workflows/operators/61-slack-command-gateway.json`
20. `workflows/operators/62-discord-relay-command-gateway.json`

Replace command-center URL placeholders and configure operator allowlists.

For Discord, read `docs/DISCORD_RELAY.md` before exposing the relay endpoint.

## 7. Import scheduled and observability workflows

21. `workflows/schedules/70-daily-autonomous-brief.json`
22. `workflows/observability/80-health-check.json`
23. `workflows/observability/81-postgres-metrics.json`

The schedule uses the n8n workflow/instance timezone. Adjust the 08:00 rule to your deployment.

## 8. Verify before publish

Run:

```bash
python scripts/validate_workflows.py
python scripts/test_contracts.py
```

Then perform the runtime smoke matrix in `docs/TESTING.md`.

Only after smoke tests pass should you publish the command center, operator gateways, schedules, and observability webhooks.
