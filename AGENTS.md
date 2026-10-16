# Agent Operating Contract

This repository is an agentic-engineering platform, so agents must preserve the platform's own guardrails while changing it.

## Authority

- Model output is a proposal, never authorization.
- Do not merge pull requests. Agent publication is limited to **draft PR creation**.
- Do not weaken approval gates, allowlists, idempotency behavior, webhook authentication, or fixed-provider write boundaries.
- Do not modify `.agent/**`, `scripts/validate_workflows.py`, or `scripts/test_contracts.py` from an autonomous coding campaign.
- Changes under `.github/workflows/**` and `workflows/actions/**` always require explicit human review.

## Workflow

1. Normalize the engineering task into the `EngineeringTask` contract.
2. Evaluate issue sensitivity and planned paths with `.agent/policy.yaml`.
3. Produce a bounded `AgentChangeSet`; never issue arbitrary shell commands from model output.
4. Apply the change-set only inside an ephemeral sandbox workspace.
5. Run only verification commands selected from trusted repository configuration.
6. Re-evaluate **actual changed paths** against policy.
7. Emit a PR evidence manifest.
8. Publish only a **draft** PR after evidence and authorization gates pass.

## Required local checks

```bash
python scripts/validate_workflows.py
python scripts/test_contracts.py
python -m unittest discover -s tests -p 'test_agentic_*.py' -v
python -m agentic_engineering.pilot --mode local
```

For the isolation proof, use Docker:

```bash
python -m agentic_engineering.pilot --mode docker
```

The Docker pilot uses no network and deliberately carries no production credentials.

## Evidence discipline

Never claim that code generation alone means success. Separate implementation, static verification, runtime verification, external-provider verification, benchmarking, simulation, and unverified design. Do not include private chain-of-thought in evidence artifacts; include conclusions, assumptions, verification output, and review hotspots only.
