# Security Model

## Trust boundaries

1. Command API ingress — Header Auth.
2. Human approval resume webhook — separate Header Auth.
3. Slack ingress — Slack Trigger plus Slack signing secret and explicit user/channel allowlists.
4. Discord ingress — Header-Auth relay only; the upstream relay must verify Discord's Ed25519 request signature.
5. Provider credentials — stored only in n8n Credentials.
6. Model boundary — models receive analysis context but not unrestricted write tools.

## Side effects

A side effect requires all of the following:

- an allowlisted explicit `action.type`;
- a deterministic payload validator;
- a human approval decision;
- a successful idempotency claim;
- a narrow provider adapter;
- an adapter-local `approved=true` guard.

Natural-language instructions cannot select an arbitrary HTTP endpoint, shell command, filesystem path, or credential.

## GitHub writes

The GitHub adapter is pinned to the GitHub REST repository host. File updates require the current blob SHA to reduce lost-update risk. Use a dedicated token scoped only to the repositories and operations required.

## Idempotency

The dispatcher claims `request_id:action_type` before executing a side effect. Repeated attempts with the same key are suppressed.

The default static ledger is portable but workflow-instance-local. The Postgres ledger uses a primary-key claim and is the recommended backend for multi-worker/restart-resistant deployments.

An ambiguous provider failure leaves the claim in place. Do not automatically reset and replay non-idempotent writes.

## Storage

The Postgres workflows use positional query parameters (`$1`, `$2`, ...) and n8n `queryReplacement` rather than interpolating user data into SQL.

## Operator allowlists

The Telegram, Slack, and Discord gateways are intentionally deny-by-default. Replace placeholder IDs with explicit operator principals before activation.

## Prohibited authority expansion

The autonomous/action layers intentionally avoid:

- Execute Command / arbitrary shell;
- arbitrary user-supplied action URLs;
- automatic permission or credential mutation;
- financial transfers;
- silent deletion/publishing;
- automatic replay of uncertain writes.

Add new powers as separately reviewed allowlisted adapters.

## Public repository hygiene

CI scans common token formats. This is a backstop, not a substitute for secret scanning and credential rotation. Never commit exported credentials or hardcoded tokens.
