#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
N8N_VERSION="${N8N_VERSION:-2.43.6}"
IMAGE="${N8N_IMAGE:-docker.n8n.io/n8nio/n8n:${N8N_VERSION}}"
PORT="${N8N_SMOKE_PORT:-5681}"
NAME="n8n-workflows-smoke-${RANDOM}-$$"
TMP="$(mktemp -d)"
STATE="$TMP/state"
IMPORTS="$TMP/imports"
EXPORTS="$TMP/exports"
KEY="$(openssl rand -hex 32)"
OWNER_EMAIL="smoke@example.invalid"
OWNER_PASSWORD="SmokeOwner$(openssl rand -hex 16)Aa1!"

cleanup() {
  docker rm -f "$NAME" >/dev/null 2>&1 || true
  # n8n writes some cache/package files as its container UID. CI runners are ephemeral,
  # so cleanup must never convert a successful smoke test into a failure.
  rm -rf "$TMP" >/dev/null 2>&1 || true
}
trap cleanup EXIT

mkdir -p "$STATE" "$IMPORTS" "$EXPORTS"
chmod 0777 "$STATE" "$EXPORTS"

index=0
while IFS= read -r -d '' file; do
  index=$((index + 1))
  printf -v prefix '%03d' "$index"
  cp "$file" "$IMPORTS/${prefix}-$(basename "$file")"
done < <(find "$ROOT/workflows" -type f -name '*.json' -print0 | sort -z)

SOURCE_COUNT="$(find "$IMPORTS" -maxdepth 1 -type f -name '*.json' | wc -l | tr -d ' ')"
if [[ "$SOURCE_COUNT" -lt 1 ]]; then
  echo "No workflow files found" >&2
  exit 1
fi

echo "Using n8n image: $IMAGE"
echo "Testing $SOURCE_COUNT workflow exports"

docker pull "$IMAGE"

start_n8n() {
  docker run -d --rm \
    --name "$NAME" \
    -p "127.0.0.1:${PORT}:5678" \
    -e N8N_ENCRYPTION_KEY="$KEY" \
    -e N8N_SECURE_COOKIE=false \
    -e N8N_DIAGNOSTICS_ENABLED=false \
    -e N8N_VERSION_NOTIFICATIONS_ENABLED=false \
    -v "$STATE:/home/node/.n8n" \
    "$IMAGE" >/dev/null
}

wait_ready() {
  for _ in $(seq 1 120); do
    if curl -fsS "http://127.0.0.1:${PORT}/healthz/readiness" >/dev/null 2>&1; then
      return 0
    fi
    sleep 2
  done
  echo "n8n did not become ready" >&2
  docker logs "$NAME" || true
  return 1
}

start_n8n
wait_ready

curl --fail-with-body -sS \
  -X POST "http://127.0.0.1:${PORT}/rest/owner/setup" \
  -H 'content-type: application/json' \
  --data "{\"email\":\"${OWNER_EMAIL}\",\"firstName\":\"Smoke\",\"lastName\":\"Runner\",\"password\":\"${OWNER_PASSWORD}\"}" \
  >/dev/null
docker stop "$NAME" >/dev/null

COMMON=(
  -e N8N_ENCRYPTION_KEY="$KEY"
  -e N8N_DIAGNOSTICS_ENABLED=false
  -e N8N_VERSION_NOTIFICATIONS_ENABLED=false
  -v "$STATE:/home/node/.n8n"
)

docker run --rm \
  "${COMMON[@]}" \
  -v "$IMPORTS:/imports:ro" \
  "$IMAGE" import:workflow --separate --input=/imports

docker run --rm \
  "${COMMON[@]}" \
  -v "$EXPORTS:/exports" \
  "$IMAGE" export:workflow --backup --output=/exports

EXPORTED_COUNT="$(find "$EXPORTS" -maxdepth 1 -type f -name '*.json' | wc -l | tr -d ' ')"
if [[ "$EXPORTED_COUNT" != "$SOURCE_COUNT" ]]; then
  echo "Round-trip count mismatch: source=$SOURCE_COUNT exported=$EXPORTED_COUNT" >&2
  find "$EXPORTS" -maxdepth 1 -type f -print >&2 || true
  exit 1
fi

start_n8n
wait_ready
curl -fsS "http://127.0.0.1:${PORT}/healthz" >/dev/null
docker stop "$NAME" >/dev/null

echo "Live n8n smoke passed: imported/exported $EXPORTED_COUNT workflows and restarted cleanly"
