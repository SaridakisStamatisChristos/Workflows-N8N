# Elite Autonomous n8n System v3

## Control plane

```text
Authenticated Command Webhook
  -> normalize + explicit action validation
  -> memory recall
  -> OpenAI route selection
  -> one specialist
  -> deterministic policy gate
       -> ready: persist + HTTP 200
       -> approval needed: HTTP 202 + signed resume URL
            -> human decision
            -> deterministic dispatcher
            -> idempotency claim
            -> one narrow write adapter
            -> completion ledger
            -> persist action result
```

## Specialists

- Research: Responses API with web search, evidence-oriented output.
- Engineering: implementation, risk, tests, and verification planning.
- Communications: drafts only; send/publish authority remains outside the model.
- GitHub read-only: repository metadata/file analysis without mutation.
- General fallback: bounded response when no specialist route is appropriate.

## Persistence backends

The command center and dispatcher refer only to workflow contracts, not storage implementation details.

Portable backend:
- workflow static-data memory;
- workflow static-data action ledger.

Durable backend:
- Postgres memory events + KV store;
- Postgres action ledger with primary-key claims.

This makes the storage layer replaceable without changing the command-center request or action contracts.

## Operators

Telegram and Slack can act as direct n8n operator surfaces.

Discord requires a small upstream interaction/message relay because n8n currently has a native Discord output node but no native Discord Trigger. The relay verifies Discord authenticity, then forwards a normalized message over Header Auth.

All operator surfaces converge on the same command-center contract.

## Scheduled autonomy

`70-daily-autonomous-brief.json` runs a read-only daily brief through the command center. It deliberately omits an action envelope, so it cannot mutate external systems.

Create further recurring jobs by following the same pattern: fixed task + fixed context + no side effect unless a separately reviewed action workflow is intentionally added.

## Observability

- `80-health-check.json` verifies OpenAI and GitHub credential/connectivity paths and returns 200/503.
- `81-postgres-metrics.json` reports memory-event and action-ledger counts, including stale claimed actions.

The metrics endpoint is authenticated because operational state is not intended to be public.

## Error recovery

The error handler captures failures. The recovery advisor may classify retryability and recommend repair, but it does not silently mutate workflows or replay non-idempotent provider actions.

## Deployment claim

Repository CI validates structure, safety invariants, and cross-workflow contracts. It does not prove that a particular n8n instance has the right credentials, provider permissions, workflow IDs, network access, or runtime node versions. Production readiness therefore requires the smoke tests in `docs/TESTING.md`.
