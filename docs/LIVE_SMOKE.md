# Live n8n Import/Boot Smoke

Static validation is not enough for workflow exports. `scripts/live_n8n_smoke.sh` performs a containerized round-trip against a real n8n runtime.

## Current pin

The harness is pinned to n8n `2.43.6`, the current release when this harness was added. Override locally with `N8N_VERSION` or `N8N_IMAGE` when testing another version.

## What it proves

1. pulls the official `docker.n8n.io/n8nio/n8n` image;
2. boots a fresh isolated n8n instance;
3. waits for `/healthz/readiness`;
4. seeds a throwaway instance owner through `/rest/owner/setup`;
5. copies every repository workflow into a flat import directory;
6. runs `import:workflow --separate` against the real CLI;
7. runs `export:workflow --backup` and requires the exported workflow count to equal the source count;
8. restarts the same n8n instance and requires readiness again.

This catches node-export incompatibilities and import/storage failures that the Python validators cannot.

## What it does not prove

The harness intentionally does not carry real credentials. It therefore does not execute OpenAI, GitHub, Gmail, Calendar, Drive, Slack, Discord, Telegram, or Postgres provider calls.

Those require the credentialed runtime smoke matrix in `docs/TESTING.md`.

## Run locally

Requirements: Docker and curl.

```bash
bash scripts/live_n8n_smoke.sh
```

Test another n8n release:

```bash
N8N_VERSION=2.43.6 bash scripts/live_n8n_smoke.sh
```

GitHub Actions runs the same harness on changes to workflow exports or the harness itself.
