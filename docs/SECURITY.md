# Security Model

## Threat model

Webhook inputs, model outputs, fetched content, and chat messages are untrusted. Primary risks include prompt injection, malformed payloads, credential disclosure, SSRF-style arbitrary HTTP behavior, duplicated side effects, and over-broad autonomous authority.

## Controls

- Authenticate command ingress with n8n Header Auth.
- Use an explicit Telegram chat allowlist in the Telegram gateway.
- Validate lengths, identifiers, routes, dates, and action types deterministically.
- Store secrets only in n8n Credentials; never commit API keys/tokens/webhook secrets.
- Prefer least-privilege/read-only credentials where possible.
- Keep GitHub analysis read-only.
- Never pass raw credential material into prompts.
- Do not expose arbitrary shell or arbitrary destination URLs to model-generated tool calls.
- Force every explicit side-effect action through human approval.
- Repeat the `approved=true` check inside every action adapter.
- Keep write adapters narrow: one capability, explicit schema, bounded input.
- Cap persistent workflow memory and error history.
- Treat recovery recommendations as proposals; automatic retry is appropriate only for clearly transient, idempotent operations.

## Action idempotency

The current adapters enforce approval and validation but do not yet provide provider-level idempotency guarantees for every service. Before high-volume production use, add a durable action ledger keyed by `request_id + action_type`, reject duplicate completed actions, and record provider result IDs. This is the next reliability hardening target.

## Deliberate exclusions

Autonomous arbitrary shell execution, unrestricted generic HTTP actions, automatic money movement, credential/permission mutation, destructive deletion, and silent publishing are outside the core system.
