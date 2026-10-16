# Agentic Engineering Platform

This layer extends the existing autonomous n8n system into a safety-first engineering workflow for selected software tasks.

## End-to-end architecture

```text
Authenticated Linear relay
  -> re-fetch issue from Linear API
  -> deterministic team/project/repository eligibility
  -> sensitive-domain classification
  -> normalized EngineeringTask
  -> planner model
  -> bounded implementer ChangeSet
  -> independent adversarial review
  -> at most one bounded repair
  -> final adversarial review
  -> deterministic evidence gate
  -> deterministic dispatch guard
  -> GitHub Actions isolated campaign runner
  -> ephemeral Docker workspace (network=none, no production secrets)
  -> path-policy check before mutation
  -> apply bounded file operations
  -> trusted repository verification commands
  -> actual-changed-path policy check
  -> PR evidence manifest
  -> verified changes materialized to an isolated branch
  -> DRAFT pull request
  -> human review / merge
```

No model receives shell access, GitHub merge authority, credential-management authority, permission to redefine verification commands, or authority to approve sensitive work.

## Linear intake

`workflows/engineering/70-linear-engineering-intake.json`

The inbound webhook is authenticated and intentionally accepts only an issue identity. The workflow then re-hydrates the issue from the fixed Linear GraphQL endpoint so title/body/labels/team/project provenance comes from Linear rather than from the relay payload.

Required configuration:

- `LINEAR_ALLOWED_TEAM_KEYS`: comma-separated team keys;
- `LINEAR_ALLOWED_PROJECT_IDS`: optional comma-separated project IDs;
- `LINEAR_REPOSITORY_MAP_JSON`: trusted team-key to `owner/repo` mapping;
- a bearer credential for the Linear API;
- Header Auth for the relay boundary.

An issue must contain `agent:auto`. Sensitive work is escalated; blocked categories are rejected. Issue existence alone never grants mutation authority.

## Coding paths

### Minimal bounded ChangeSet generator

`workflows/engineering/71-change-set-generator.json`

This is the smallest implementation-proposal surface. The model may return only a bounded file-operation contract:

```json
{
  "task_id": "linear-ENG-123",
  "summary": "...",
  "confidence": 0.82,
  "operations": [
    {"op": "write_file", "path": "src/example.py", "content": "..."}
  ]
}
```

It cannot supply verification commands or authorize sensitive paths.

### Reviewed coding campaign

`workflows/engineering/73-reviewed-coding-campaign.json`

For higher-quality autonomous work, the preferred path is intentionally role-separated:

1. a planner interprets the task and states constraints, expected files, tests, risks, and completion criteria;
2. an implementer emits a bounded ChangeSet;
3. an independent adversarial reviewer attempts to falsify the proposal;
4. when the reviewer returns `repair`, exactly one bounded repair pass is allowed;
5. a final adversarial reviewer either returns `accept` or `escalate`;
6. only an accepted ChangeSet proceeds to deterministic execution.

Model review is advisory evidence, never authorization. The deterministic worker still re-validates every planned and actual changed path and runs only repository-owned verification commands.

`workflows/engineering/74-reviewed-campaign-orchestrator.json` connects the reviewed campaign to the fixed campaign-dispatch workflow through a deterministic evidence gate.

## Isolated execution

`agentic_engineering/sandbox.py` implements the execution boundary.

For Docker mode, verification runs with:

- `--network none`;
- all Linux capabilities dropped;
- `no-new-privileges`;
- PID, memory, CPU, and wall-clock limits;
- read-only container root filesystem;
- a writable ephemeral workspace mount only;
- no production credentials injected by the platform;
- a digest-pinned Python sandbox image.

The automatic campaign path forcibly clears `human_review_granted`. Sensitive paths therefore cannot be made writable merely by placing a field in model/task JSON.

## Self-protection

`.agent/policy.yaml` deterministically protects the guardrails and publication control state, including:

- `.git`, `.git/**`, `.gitignore`, `.gitattributes`, `.gitmodules`;
- `.agent/**`;
- `scripts/validate_workflows.py`;
- `scripts/test_contracts.py`;
- `agentic_engineering/**`.

CI definitions and external write adapters are review-required. Task-local allow/forbid patterns are evaluated in addition to repository-global policy.

## Trusted verification

`.agent/verification.yaml` owns the verification command profiles. Issue text and model output cannot define executable commands.

The platform profile runs:

```text
python scripts/validate_workflows.py
python scripts/test_contracts.py
python -m unittest discover -s tests -p 'test_agentic_*.py' -v
```

## Draft PR publication

`.github/workflows/agentic-campaign-runner.yml` is the controlled write lane.

It:

1. receives normalized task JSON and bounded change-set JSON;
2. executes and verifies inside the Docker sandbox;
3. materializes only verified changed files back to the checked-out workspace;
4. creates a new `agent/...` branch;
5. pushes the branch;
6. creates a **draft** PR;
7. uploads the evidence artifact.

It contains no merge step. Duplicate publication for the same stable task ID is rejected.

`workflows/engineering/72-agent-campaign-dispatch.json` dispatches only the fixed campaign-runner endpoint in this repository and deliberately does not auto-retry an ambiguous dispatch outcome.

## PR evidence

The generated `pr-evidence.json` records:

- task/source provenance;
- repository/base ref;
- change summary;
- changed files;
- exact verification commands and results;
- deterministic policy checks;
- optional adversarial-review evidence;
- known failures;
- risk areas and sensitive paths;
- assumptions;
- review hotspots;
- agent confidence when provided;
- explicit human-judgment requirements;
- wall-clock/retry/policy metrics;
- verification level.

The rendered PR body intentionally contains conclusions and evidence, not private chain-of-thought.

## Evaluation lab

`benchmarks/tasks/*.yaml` contains JSON-compatible YAML task specifications so the harness remains dependency-free.

`python -m agentic_engineering.benchmark --mode docker` executes the corpus and checks expected outcomes.

The initial corpus contains three **SIMULATED** fixture controls:

1. a valid code fix that must pass verification;
2. a forbidden test mutation that policy must reject;
3. an allowed but incorrect change that verification must block.

The fixture change-sets are canned, so `quality_benchmark_task_count` is explicitly `0`. These tasks measure pipeline and safety mechanics, **not autonomous coding quality**. Real historical tasks can be added later without changing the runner contract.

`agentic_engineering/evaluate.py` keeps measured fields, manually supplied reviewer metrics, and inferred fields separate. Developer satisfaction is never inferred.

## Verification commands

```bash
python -m unittest discover -s tests -p 'test_agentic_*.py' -v
python -m agentic_engineering.pilot --mode local
python -m agentic_engineering.benchmark --mode local
```

CI additionally runs the Docker isolation pilot and the repository's pinned real-n8n import/export/restart smoke.

## Known limitations

- The public repository does not contain real n8n historical engineering tasks or internal reviewer/adoption data.
- Linear/OpenAI/GitHub credentials and a trusted Linear relay must be configured by the deployer; no provider credentials are committed.
- The current orchestrated coding target is deliberately allowlisted to this repository. Multi-repository support should add explicit repository-specific policies rather than broadening authority.
- The fixture benchmark is not evidence that an LLM can solve historical n8n tasks.
- The reviewed campaign is structurally/runtime validated but still lacks credentialed end-to-end execution against a real Linear issue and real model call in deployed n8n.
- Human reviewer acceptance, rework, and satisfaction metrics require actual reviewers and are represented as manual collection fields only.
