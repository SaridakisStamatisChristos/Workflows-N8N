# Elite Autonomous n8n System

## Architecture

The system follows a control-plane pattern:

`Authenticated Command Webhook → Input Normalization → Memory Recall → AI Router → Specialist Sub-workflow → Deterministic Policy Gate → Ready Response OR Human Approval Wait → Memory Write`

### Why compositional workflows

n8n supports parent workflows calling independently testable sub-workflows through `Execute Sub-workflow` / `Execute Sub-workflow Trigger`. This repository uses that pattern so each specialist can be tested and upgraded without destabilizing the whole system.

## Specialists

### Research
Uses the OpenAI Responses API with web search enabled. It must separate factual findings from inference and return structured JSON.

### Engineering
Produces implementation plans, tests, risks, and verification steps. It does not claim repository mutations unless evidence is present.

### Communications
Drafts messages and briefs. Send/publish intent is always marked as requiring approval.

### GitHub Read-only
Reads repository metadata and one requested path through GitHub REST, then analyzes it. No write endpoint exists in this workflow.

## Memory

The first portable memory backend uses `$getWorkflowStaticData('global')` in a dedicated sub-workflow and caps retained history. This removes external database requirements while giving cross-execution state for production executions. For larger deployments, replace this module with Postgres/Redis/vector storage while preserving the input/output contract.

## Human approval

High-risk or explicitly approval-required results return HTTP 202. The response contains n8n's execution-specific signed resume URL. The execution waits up to 24 hours for a POST body like:

```json
{"approved": true, "note": "Reviewed"}
```

The approval outcome is written to memory. Write-capable adapters should be connected only after this node.

## Security boundary

- Webhook ingress uses Header Auth.
- OpenAI/GitHub API keys are n8n credentials, not JSON literals.
- The GitHub specialist is read-only.
- No arbitrary shell/command execution exists.
- No generic arbitrary-URL action tool is exposed to the model.
- High-risk results cannot silently bypass the deterministic approval rule.

## Next extension layer

The safe next additions are dedicated allowlisted action sub-workflows for GitHub issues/PR comments, Gmail drafts/sends, Calendar events, Drive document operations, and Telegram/Slack operator ingress. Each should have explicit schemas, least-privilege credentials, idempotency keys, dry-run mode, and approval requirements for irreversible operations.
