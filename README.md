# Workflows-N8N

Production-oriented n8n workflows, reusable automation systems, and bounded autonomous orchestration patterns.

## Elite systems

### Elite AI Ops Orchestrator
`workflows/core/elite-ai-ops-orchestrator.json`

Authenticated webhook → deterministic validation → planner → adversarial critic → final synthesis → policy/approval gate.

### Elite Autonomous System v3
`workflows/autonomous/00-autonomous-command-center.json`

A compositional control plane with:

- bounded memory and interchangeable persistence backends;
- AI routing into independent research, engineering, communications, GitHub, and general specialists;
- OpenAI Responses API + current-web research;
- deterministic risk and human-approval policy;
- idempotent approved-action execution;
- Gmail, Google Calendar, Google Drive, Telegram, Slack, Discord, and GitHub write adapters;
- Telegram and Slack direct operator gateways;
- authenticated Discord relay gateway;
- scheduled autonomous read-only briefs;
- dependency health checks and Postgres operations metrics;
- centralized error capture and bounded recovery advice;
- structural, safety, and contract CI.

## Repository layout

```text
workflows/
  core/
  autonomous/
  actions/
  operators/
  storage/
  schedules/
  observability/
docs/
examples/
scripts/
.github/workflows/
```

## Safety model

The LLM never receives unrestricted write authority.

1. models research, analyze, draft, and route;
2. a caller must provide an explicit allowlisted `action` envelope for a side effect;
3. any action forces a human-approval wait;
4. the signed n8n resume webhook resumes only after the operator decision;
5. the deterministic dispatcher claims an idempotency key before execution;
6. exactly one narrow action adapter runs;
7. each adapter independently requires `approved=true`;
8. the completion ledger records the result using the original claimed key.

Natural-language intent such as “send this email” does **not** send anything by itself.

## Persistence

Two interchangeable implementations preserve the same workflow contracts:

- portable/default: `05-memory-store.json` + `55-action-ledger.json` using workflow static data;
- durable: `06-postgres-memory-store.json` + `56-postgres-action-ledger.json`.

Use Postgres for multi-worker, restart-resistant, or higher-volume deployments.

## Operator surfaces

- Telegram: native trigger.
- Slack: native Slack Trigger; configure a Slack signing secret and explicit user/channel allowlists.
- Discord: n8n has no native Discord Trigger, so the repository uses a Header-Auth relay contract. The upstream relay must verify Discord's request signature before forwarding a normalized event.

## Validation

```bash
python scripts/validate_workflows.py
python scripts/test_contracts.py
```

The same checks run in GitHub Actions on every push to `main` and every pull request.

## Deployment status

The repository exports are structurally and contract validated. They still require instance-specific n8n workflow-ID bindings, credentials, allowlists, URLs, and runtime smoke tests before production publication.

Start with `docs/IMPORT_ORDER.md`, then read `docs/AUTONOMOUS_SYSTEM.md`, `docs/ACTIONS.md`, `docs/SECURITY.md`, and `docs/TESTING.md`.

No API keys, OAuth secrets, webhook secrets, passwords, or tokens are committed to this repository.
