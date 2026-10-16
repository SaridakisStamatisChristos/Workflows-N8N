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

## Optional deliberation review

`workflows/autonomous/40-deliberation-review.json` adds a bounded review layer for hard or high-stakes analyses. It consumes the original task/context plus a primary specialist candidate, then runs:

1. an adversarial specialist that searches for unsupported claims, hidden risks, contradictions, and missing evidence;
2. an independent arbiter that synthesizes the primary candidate and critique into a final defensible result.

The module contains no provider write nodes and no sub-workflow action dispatch. It is intentionally **not** wired into every command-center request because it adds two high-effort model calls. Insert it after a primary specialist and before the deterministic policy gate when the extra review cost is justified.

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

## Verification layers

1. `validate_workflows.py` checks structure and local safety invariants.
2. `test_contracts.py` checks cross-workflow platform contracts.
3. `live_n8n_smoke.sh` imports/exports the full workflow set through a real pinned n8n container and verifies restart readiness.
4. credentialed smoke tests validate provider-specific behavior on the target deployment.

Repository checks provide evidence that the exports are structurally coherent and importable on the pinned n8n version. They do not prove that a particular deployment has correct credentials, permissions, network access, or provider configuration.
