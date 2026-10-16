# Import and Wiring Order

## 1. Import foundational sub-workflows

1. `workflows/autonomous/05-memory-store.json`
2. `workflows/autonomous/10-research-specialist.json`
3. `workflows/autonomous/20-engineering-specialist.json`
4. `workflows/autonomous/30-communications-specialist.json`
5. `workflows/autonomous/35-github-readonly-specialist.json`
6. `workflows/autonomous/90-error-handler.json`
7. `workflows/autonomous/91-recovery-advisor.json`

## 2. Import write adapters

8. `workflows/actions/51-gmail-send-approved.json`
9. `workflows/actions/52-calendar-create-approved.json`
10. `workflows/actions/53-drive-create-text-approved.json`
11. `workflows/actions/54-telegram-notify-approved.json`
12. `workflows/actions/50-approved-action-dispatcher.json`

Bind the dispatcher placeholders to the four imported action workflow IDs.

## 3. Import command center

13. `workflows/autonomous/00-autonomous-command-center.json`

Bind these placeholders:

- `REPLACE_MEMORY_WORKFLOW_ID`
- `REPLACE_RESEARCH_WORKFLOW_ID`
- `REPLACE_ENGINEERING_WORKFLOW_ID`
- `REPLACE_COMMUNICATIONS_WORKFLOW_ID`
- `REPLACE_GITHUB_WORKFLOW_ID`
- `REPLACE_ACTION_DISPATCHER_WORKFLOW_ID`

## 4. Assign credentials

- Command webhook: Header Auth.
- OpenAI nodes: HTTP Bearer Auth with OpenAI API key.
- GitHub read-only specialist: HTTP Bearer Auth with least-privilege read token.
- Gmail action: Gmail OAuth2 credential.
- Calendar action: Google Calendar OAuth2 credential.
- Drive action: Google Drive OAuth2 credential.
- Telegram action/gateway: Telegram bot credential.

Never place static secrets in Code or HTTP Request headers.

## 5. Import Telegram operator gateway

14. `workflows/operators/60-telegram-command-gateway.json`

Edit `REPLACE_ALLOWED_CHAT_ID`, replace `REPLACE_COMMAND_CENTER_WEBHOOK_URL`, and assign an HTTP Header Auth credential matching the command webhook secret.

## 6. Verify before publish

Test each supporting workflow independently. Then test command-center requests with and without an action envelope. Confirm that an action returns 202, pauses, rejects a false approval, and executes only after true approval.

Finally publish/activate only the workflows you intend to expose.
