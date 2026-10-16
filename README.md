# Workflows-N8N

A curated repository of production-oriented n8n workflows, reusable automation systems, and autonomous orchestration patterns.

## Current systems

### 1. Elite AI Ops Orchestrator
`workflows/core/elite-ai-ops-orchestrator.json`

A secure webhook-driven multi-pass AI workflow: validation → planner → adversarial critic → final synthesis → deterministic risk/approval gate.

### 2. Elite Autonomous Core v1
`workflows/autonomous/`

A compositional autonomous system built around an n8n command center and independently testable specialist sub-workflows:

- `00-autonomous-command-center.json` — routing, memory retrieval, policy gate, approval/resume.
- `05-memory-store.json` — bounded persistent workflow memory using n8n static data.
- `10-research-specialist.json` — OpenAI Responses API + web search.
- `20-engineering-specialist.json` — architecture/code/algorithm analysis and verification planning.
- `30-communications-specialist.json` — drafting only; sending/publishing is approval-gated.
- `35-github-readonly-specialist.json` — read-only GitHub metadata/file analysis.
- `90-error-handler.json` — centralized error capture ring buffer.

See `docs/AUTONOMOUS_SYSTEM.md` and `docs/IMPORT_ORDER.md`.

## Design principles

1. Deterministic validation and policy checks surround model calls.
2. Models may recommend actions; irreversible side effects require explicit approval.
3. Credentials are never embedded in committed workflow JSON.
4. Large systems are decomposed into independently testable sub-workflows.
5. Read-only integrations are preferred before write-capable adapters.
6. Every workflow should have an observable failure mode and a recovery path.

## Status

The autonomous system is intentionally **safe-by-default**. It can research, analyze, route, remember bounded context, inspect GitHub read-only, draft communications, and pause for human approval. Write-capable Gmail/GitHub/Calendar/Drive and chat control adapters are the next extension layer and should bind only after credentials and allowlists are configured.
