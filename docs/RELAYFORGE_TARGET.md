# RelayForge target integration

RelayForge is an allowlisted external target for the agentic engineering campaign runner.

## Authority boundary

The control plane remains in `SaridakisStamatisChristos/Workflows-N8N`. The target repository is `SaridakisStamatisChristos/RelayForge`. Model output never authorizes repository access, verification commands, protected-path changes, publication, or merge.

A RelayForge campaign requires a fine-grained `RELAYFORGE_GITHUB_TOKEN` stored as a GitHub Actions secret in Workflows-N8N. Scope it only to RelayForge with the minimum permissions needed to push an isolated `agent/<task-id>` branch and create a pull request. The token is used by checkout/Git/GitHub CLI only. The campaign sandbox copies the target without `.git`, runs with a sanitized environment, and therefore does not receive the token.

## Trusted execution path

1. The dispatch contract must name `SaridakisStamatisChristos/RelayForge` and `base_ref=main`.
2. The repository must already be present in the control-plane allowlist.
3. RelayForge is checked out independently from the Workflows-N8N control plane.
4. `pnpm install --frozen-lockfile` runs before model-sandbox execution so dependency resolution is not granted network access inside the sandbox.
5. The trusted verifier image is built from `docker/relayforge-verifier.Dockerfile` with pinned pnpm and local PostgreSQL support.
6. The bounded change-set is copied into an ephemeral workspace and verified with Docker networking disabled.
7. Verification commands come from RelayForge's repository-controlled `.agent/verification.yaml`, never from issue or model text.
8. The verifier image starts a fresh local PostgreSQL instance on a Unix socket inside each networkless container, allowing both `default` and `database` RelayForge profiles to execute without external network access.
9. Only a fully verified change-set is materialized back into the target checkout.
10. Publication is limited to a new `agent/<task-id>` branch and a **draft PR**. The workflow contains no merge action.

## Human gate before the first real campaign

The RelayForge baseline must first exist on RelayForge `main`. While its zero-to-hero implementation is still an unmerged draft PR, the cross-repository campaign path is implemented but cannot truthfully be demonstrated against the intended baseline. Do not copy baseline files into `main` merely to manufacture a pilot result.

After the baseline is accepted by a human, configure `RELAYFORGE_GITHUB_TOKEN` and dispatch an EngineeringTask with the `agent:auto` authorization label, bounded allowed/forbidden paths, and either RelayForge's `default` or `database` verification profile. Preserve the workflow artifact and resulting draft PR as execution evidence.
