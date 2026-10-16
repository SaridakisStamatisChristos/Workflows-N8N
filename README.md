# Workflows-N8N

Production-oriented n8n workflows, reusable automation systems, and bounded autonomous orchestration patterns.

## Elite systems

### Elite AI Ops Orchestrator
`workflows/core/elite-ai-ops-orchestrator.json`

Authenticated webhook → validation → planner → adversarial critic → final synthesis → deterministic approval gate.

### Elite Autonomous System v2
`workflows/autonomous/00-autonomous-command-center.json`

A compositional control plane with:

- bounded persistent memory;
- AI routing into independent specialists;
- current-web research through OpenAI Responses web search;
- engineering analysis and verification planning;
- communications drafting;
- read-only GitHub inspection;
- deterministic risk policy;
- signed human approval/resume flow;
- explicit approved-action contracts;
- Gmail, Google Calendar, Google Drive, and Telegram write adapters;
- Telegram operator gateway;
- centralized error capture and bounded recovery analysis.

## Repository layout

```text
workflows/
  core/
    elite-ai-ops-orchestrator.json
  autonomous/
    00-autonomous-command-center.json
    05-memory-store.json
    10-research-specialist.json
    20-engineering-specialist.json
    30-communications-specialist.json
    35-github-readonly-specialist.json
    90-error-handler.json
    91-recovery-advisor.json
  actions/
    50-approved-action-dispatcher.json
    51-gmail-send-approved.json
    52-calendar-create-approved.json
    53-drive-create-text-approved.json
    54-telegram-notify-approved.json
  operators/
    60-telegram-command-gateway.json
docs/
examples/
```

## Safety model

The LLM never receives an unrestricted action tool. Read/write authority is split:

1. models research, analyze, draft, and route;
2. an explicit request `action` envelope names one allowlisted side effect;
3. any action forces human approval;
4. the approval callback resumes the suspended n8n execution;
5. a deterministic dispatcher calls exactly one narrow adapter;
6. every adapter independently refuses execution unless `approved=true`.

Natural-language requests such as “send this email” **do not send anything** unless the request also contains a valid explicit action contract and the human approves the preview.

## Setup

Read `docs/IMPORT_ORDER.md`, `docs/AUTONOMOUS_SYSTEM.md`, `docs/ACTIONS.md`, and `docs/SECURITY.md` before publishing workflows.

No credentials, API keys, webhook secrets, or tokens are committed to this repository.
