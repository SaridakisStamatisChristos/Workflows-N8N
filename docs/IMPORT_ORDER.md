# Import and Wiring Order

## 1. Import foundational sub-workflows

1. `workflows/autonomous/05-memory-store.json`
2. `workflows/autonomous/10-research-specialist.json`
3. `workflows/autonomous/20-engineering-specialist.json`
4. `workflows/autonomous/30-communications-specialist.json`
5. `workflows/autonomous/35-github-readonly-specialist.json`
6. `workflows/autonomous/90-error-handler.json`
7. `workflows/autonomous/91-recovery-advisor.json`

## 2. Import write adapters and action ledger

8. `workflows/actions/51-gmail-send-approved.json`
9. `workflows/actions/52-calendar-create-approved.json`
10. `workflows/actions/53-drive-create-text-approved.json`
11. `workflows/actions/54-telegram-notify-approved.json`
12. `workflows/actions/55-action-ledger.json`
13. `workflows/actions/50-approved-action-dispatcher.json`

Bind the dispatcher placeholders:

- `REPLACE_GMAIL_ACTION_WORKFLOW_ID`
- `REPLACE_CALENDAR_ACTION_WORKFLOW_ID`
- `REPLACE_DRIVE_ACTION_WORKFLOW_ID`
- `REPLACE_TELEGRAM_ACTION_WORKFLOW_ID`
- `REPLACE_ACTION_LEDGER_WORKFLOW_ID`

The ledger suppresses repeated `request_id + action_type` claims. A failed/crashed action remains claimed by design; inspect it before using the ledger `reset` operation. Safety takes priority over automatic replay of non-idempotent writes.

## 3. Import command center

14. `workflows/autonomous/00-autonomous-command-center.json`

Bind:

- `REPLACE_MEMORY_WORKFLOW_ID`
- `REPLACE_RESEARCH_WORKFLOW_ID`
- `REPLACE_ENGINEERING_WORKFLOW_ID`
- `REPLACE_COMMUNICATIONS_WORKFLOW_ID`
- `REPLACE_GITHUB_WORKFLOW_ID`
- `REPLACE_ACTION_DISPATCHER_WORKFLOW_ID`

## 4. Assign credentials

- Command Webhook: Header Auth.
- Wait for Human Approval: incoming Header Auth (bind explicitly; it is a second webhook boundary).
- OpenAI nodes: HTTP Bearer Auth with OpenAI API key.
- GitHub read-only specialist: HTTP Bearer Auth with least-privilege read token.
- Gmail action: Gmail OAuth2 credential.
- Calendar action: Google Calendar OAuth2 credential.
- Drive action: Google Drive OAuth2 credential.
- Telegram action/gateway: Telegram bot credential.

Never place static secrets in Code nodes or HTTP Request header parameters.

## 5. Import Telegram operator gateway

15. `workflows/operators/60-telegram-command-gateway.json`

Edit `REPLACE_ALLOWED_CHAT_ID`, replace `REPLACE_COMMAND_CENTER_WEBHOOK_URL`, assign an HTTP Header Auth credential matching the command webhook secret, and assign the Telegram bot credential.

## 6. Verify before publish

Run `python scripts/validate_workflows.py` locally; the same validator runs in GitHub Actions.

Then test each supporting workflow independently. Test command-center requests with and without an action. Confirm that an action returns 202, pauses, rejects false approval, executes only after true approval, and suppresses a second attempt with the same `request_id + action_type`.

Finally publish/activate only the workflows you intend to expose.
