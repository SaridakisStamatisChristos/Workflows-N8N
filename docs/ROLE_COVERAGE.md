# n8n Agentic Engineering Platform Engineer — Repository Coverage

Target role: **Agentic Engineering Platform Engineer**.

This matrix is evidence-oriented. It does not convert fixture simulation into real organizational adoption, historical-task quality, or human satisfaction evidence.

| Requirement | Repository evidence | Current evidence class | Coverage | Remaining gap |
|---|---|---|---:|---|
| Safe task categories | `.agent/policy.yaml`, Linear eligibility gate | IMPLEMENTED + negative tests | Strong | Needs real team tuning |
| Human review boundaries | sensitive classification, review-required paths, draft-only publication | IMPLEMENTED | Strong | Human process outside repo |
| Isolated execution | digest-pinned Docker sandbox with no network/caps/provider secrets | CI RUNTIME VERIFIED | Strong | Not a hardened multi-tenant sandbox |
| Linear issue intake | API re-hydration + team/project/repo allowlists + `agent:auto` | IMPLEMENTED | Strong | External credentialed smoke pending |
| Agent planning | reviewed campaign planner contract | IMPLEMENTED + workflow tests | Strong | Real-task usefulness not benchmarked |
| Agent coding | bounded ChangeSet implementer + deterministic worker | IMPLEMENTED | Strong | Real-task quality not benchmarked |
| Independent adversarial review | initial reviewer + final reviewer | IMPLEMENTED + workflow tests | Strong | Model-behavior quality needs real campaigns |
| Bounded repair | exactly one repair path before final review | IMPLEMENTED + workflow tests | Strong | Need empirical repair-success data |
| Automated testing | trusted verification profiles | CI RUNTIME VERIFIED | Strong | Broader language/toolchain profiles |
| Draft PR generation | campaign runner `gh pr create --draft` | IMPLEMENTED | Strong | Credentialed end-to-end publication pilot |
| Repo instructions | `AGENTS.md` | IMPLEMENTED | Strong | Target-repo-specific refinement |
| Agent playbooks | `.agent/policy.yaml`, `.agent/verification.yaml` | IMPLEMENTED | Strong | More monorepo context packs |
| Ownership metadata | `.agent/ownership.yaml` | IMPLEMENTED | Moderate/Strong | Map to real CODEOWNERS/team IDs |
| GitHub integration | Actions dispatch, branch/commit/draft PR pipeline | IMPLEMENTED | Strong | Credentialed end-to-end pilot |
| CI integration | agentic CI + structural validation + pinned live n8n smoke | CI VERIFIED | Strong | Accumulate longitudinal history |
| PR evidence | JSON schema + renderer + adversarial review evidence | IMPLEMENTED + generated CI artifact | Strong | Reviewer feedback loop |
| Sensitive path guardrails | planned + actual path checks; Git control-state protection | IMPLEMENTED + negative tests | Strong | Repository-specific policy expansion |
| Historical task benchmarks | generic task schema/runner exists | INFRASTRUCTURE IMPLEMENTED | Partial | Real historical tasks unavailable publicly |
| Failure-mode tracking | benchmark outcomes + known failures + policy results | IMPLEMENTED | Moderate/Strong | Persistent longitudinal dataset |
| CI pass metrics | evaluation schema supports measured pass rate | IMPLEMENTED | Moderate | Real multi-run history |
| Reviewer acceptance metrics | manual field separated from inferred data | COLLECTION MECHANISM | Partial | Needs real reviewers |
| Rework metrics | retry/repair/evidence fields | COLLECTION MECHANISM | Partial | Needs real campaigns |
| Developer satisfaction | intentionally not inferred | COLLECTION MECHANISM ONLY | Partial | Requires actual developers |
| Safety / least privilege | no model shell/auth/merge authority; network-off sandbox; protected guardrails | CI RUNTIME VERIFIED for fixture path | Strong | Hardened sandbox technology could go further |
| Written technical docs | `AGENTS.md`, this document, `AGENTIC_ENGINEERING.md` | IMPLEMENTED | Strong | Keep synchronized with future changes |

## Claim boundary

The repository can demonstrate platform engineering, planner/implementer/reviewer orchestration, deterministic guardrails, sandbox mechanics, CI integration, GitHub draft-PR mechanics, evidence design, and evaluation infrastructure.

It cannot yet demonstrate production use inside n8n, adoption by n8n engineers, cross-functional influence inside n8n, real historical-task coding quality, reviewer acceptance, or developer satisfaction without real organizational access and human data.
