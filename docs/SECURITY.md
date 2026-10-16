# Security Model

## Threat model

This repository assumes webhook inputs and model outputs are untrusted. Prompt injection, malformed input, accidental credential disclosure, and over-broad autonomous side effects are treated as primary risks.

## Controls

- Authenticate ingress.
- Validate lengths, formats, routes, and repository names deterministically.
- Keep secrets exclusively in n8n Credentials.
- Prefer read-only tokens.
- Never pass raw secrets into model prompts.
- Require human approval for high/critical risk or send/publish/delete/purchase/permission-changing actions.
- Cap persistent memory to prevent unbounded retention.
- Configure an error workflow and inspect failed executions.
- Add idempotency keys before enabling write-capable adapters.

## Deliberate exclusions

Autonomous arbitrary shell execution, unrestricted HTTP actions, automatic money movement, credential/permission mutation, and silent publishing are not part of the autonomous core.
