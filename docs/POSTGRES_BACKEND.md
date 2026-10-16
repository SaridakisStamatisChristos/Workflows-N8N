# Postgres Persistence Backend

The durable workflows preserve the same input contracts as the portable static-data backends.

## Memory

`workflows/storage/06-postgres-memory-store.json`

Inputs:

- `operation`: `append | put | get | recent | find_request`
- `request_id`
- `key`
- `value`
- `limit`

Tables are created idempotently:

- `n8n_elite_memory_events`
- `n8n_elite_memory_kv`

All user values are passed through positional Postgres query parameters.

## Action ledger

`workflows/storage/56-postgres-action-ledger.json`

Inputs:

- `operation`: `claim | complete | fail | get | reset`
- `key`
- `value`

Table:

- `n8n_elite_action_ledger`

`claim` uses `INSERT ... ON CONFLICT DO NOTHING` under a primary key. This gives an atomic single-winner claim across concurrent workers.

## Wiring

To use Postgres:

1. import both storage workflows;
2. bind a Postgres credential to every Postgres node;
3. set `REPLACE_MEMORY_WORKFLOW_ID` in the command center to the Postgres memory workflow;
4. set `REPLACE_ACTION_LEDGER_WORKFLOW_ID` in the dispatcher to the Postgres ledger workflow.

No other command-center or adapter changes are required.

## Operations

`workflows/observability/81-postgres-metrics.json` reports:

- total memory events;
- total/claimed/completed/failed actions;
- claims older than one hour;
- age of the oldest live claim.

A stale claim means an operator should investigate the provider outcome before resetting it.
