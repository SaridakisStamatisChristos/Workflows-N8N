# Elite Autonomous n8n System v2

## Architecture

```text
Authenticated Command Webhook
  → deterministic input/action validation
  → bounded memory recall
  → OpenAI router
  → one specialist
      research | engineering | communications | GitHub read-only | general
  → deterministic policy gate
      → no approval needed: persist + HTTP 200
      → approval/action present: HTTP 202 + signed resume URL
          → Wait up to 24h
          → human approve/reject
          → if approved action exists
              → deterministic action dispatcher
              → Gmail | Calendar | Drive | Telegram adapter
              → persist action result
```

## Specialists

### Research
Uses the OpenAI Responses API with built-in web search. It separates findings/sources and cannot execute external side effects.

### Engineering
Produces implementation plans, tests, risks, and verification steps. It cannot claim repository changes unless evidence is supplied.

### Communications
Drafts messages/briefs. Sending remains a separate approved action.

### GitHub read-only
Validates `owner/repo`, fetches repository metadata plus one requested path through GitHub REST, and analyzes the supplied data. No GitHub write endpoint exists in this specialist.

## Memory

The portable default uses `$getWorkflowStaticData('global')` inside the dedicated memory sub-workflow. It implements append/put/get/recent/find_request and caps the event ring buffer at 200 entries.

For large or multi-instance deployments, replace the memory implementation behind the same workflow contract with Postgres/Redis/vector storage.

## Write authority

Write authority is deliberately separated from reasoning. An LLM does not get arbitrary HTTP, shell, Gmail, Calendar, Drive, Telegram, or GitHub-write tools.

An external caller must provide an explicit allowlisted `action.type` and payload. The command center forces approval whenever an action exists. The approval preview contains the resolved action. Only after the signed resume callback receives `approved=true` can the deterministic dispatcher call a narrow write adapter.

Every adapter repeats the `approved=true` invariant and validates its own payload. This is defense in depth against routing/wiring mistakes.

## Operator control

The primary API is the authenticated command webhook. `workflows/operators/60-telegram-command-gateway.json` provides a Telegram front-end with a fixed chat allowlist and forwards commands through authenticated HTTP to the command center.

## Reliability and recovery

- external calls use retry/timeout controls where appropriate;
- malformed model output is contract-checked;
- `90-error-handler.json` captures a bounded error ring buffer;
- `91-recovery-advisor.json` classifies failures and proposes bounded remediation, but does not mutate workflows or automatically retry non-idempotent actions.

## Deliberate boundaries

The system does not provide arbitrary shell execution, unrestricted URL fetching as an action tool, financial transfers, permission/credential mutation, or automatic publishing/deletion. Add new actions as separately reviewed allowlisted adapters rather than expanding the model's raw authority.
