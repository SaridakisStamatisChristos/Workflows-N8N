# n8n Agentic Engineering Platform Engineer — Repository Coverage

Target role: **Agentic Engineering Platform Engineer**.

This matrix is evidence-oriented. It does not convert fixture simulation into real organizational adoption, historical-task quality, or human satisfaction evidence.

| Requirement | Repository evidence | Current evidence class | Coverage | Remaining gap |
|---|---|---|---:|---|
| Safe task categories | `.agent/policy.yaml`, Linear eligibility gate | IMPLEMENTED + local negative tests | Strong | Needs real team tuning |
| Human review boundaries | sensitive classification, review-required paths, draft-only publication | IMPLEMENTED | Strong | Human process outside repo |
| Isolated execution | Docker sandbox with no network/caps/secrets | IMPLEMENTED; CI runtime gate | Strong | Not a hardened multi-tenant sandbox |
| Linear issue intake | API re-hydration + allowlists + `agent:auto` | IMPLEMENTED | Strong | External credentialed smoke pending |
| Agent coding | bounded ChangeSet model workflow + deterministic worker | IMPLEMENTED | Strong | Real-task quality not benchmarked |
| Automated testing | trusted verification profiles | IMPLEMENTED + local runtime | Strong | Broader language/toolchain profiles |
| Draft PR generation | campaign runner `gh pr create --draft` | IMPLEMENTED | Strong | External runner execution evidence required |
| Repo instructions | `AGENTS.md` | IMPLEMENTED | Strong | Target-repo-specific refinement |
| Agent playbooks | `.agent/policy.yaml`, `.agent/verification.yaml` | IMPLEMENTED | Strong | More monorepo context packs |
| Ownership metadata | `.agent/ownership.yaml` | IMPLEMENTED | Moderate/Strong | Map to real CODEOWNERS/team IDs |
| GitHub integration | Actions dispatch, branch/commit/draft PR pipeline | IMPLEMENTED | Strong | Credentialed end-to-end pilot |
| CI integration | agentic CI + existing validation/live n8n CI | IMPLEMENTED | Strong | Observe feature-branch runs |
| PR evidence | JSON schema + renderer | IMPLEMENTED + local generation | Strong | Reviewer feedback loop |
| Sensitive path guardrails | deterministic planned + actual path checks | IMPLEMENTED + negative tests | Strong | Repository-specific policy expansion |
| Historical task benchmarks | generic task schema/runner exists | INFRASTRUCTURE IMPLEMENTED | Partial | Real historical tasks unavailable publicly |
| Failure-mode tracking | benchmark outcomes + known failures + policy results | IMPLEMENTED | Moderate/Strong | Persistent longitudinal dataset |
| CI pass metrics | evaluation schema supports measured pass rate | IMPLEMENTED | Moderate | Real multi-run history |
| Reviewer acceptance metrics | manual field separated from inferred data | COLLECTION MECHANISM | Partial | Needs real reviewers |
| Rework metrics | retry count/evidence fields | COLLECTION MECHANISM | Partial | Needs real campaigns |
| Developer satisfaction | intentionally not inferred | COLLECTION MECHANISM ONLY | Partial | Requires actual developers |
| Safety / least privilege | no model shell, no model auth, network-off sandbox, protected guardrails | IMPLEMENTED | Strong | Hardened sandbox technology could go further |
| Written technical docs | `AGENTS.md`, this document, `AGENTIC_ENGINEERING.md` | IMPLEMENTED | Strong | Keep synchronized with future changes |

## Claim boundary

The repository can demonstrate platform engineering, orchestration, guardrails, sandbox mechanics, CI integration, GitHub draft-PR mechanics, evidence design, and evaluation infrastructure.

It cannot demonstrate cross-functional influence inside n8n, adoption by n8n engineers, production impact inside n8n, or developer satisfaction without real organizational access and human data.
