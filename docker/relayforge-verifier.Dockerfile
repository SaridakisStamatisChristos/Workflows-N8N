FROM node:22-bookworm-slim

ARG PNPM_VERSION=10.18.3

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates postgresql util-linux \
    && rm -rf /var/lib/apt/lists/* \
    && npm install --global "pnpm@${PNPM_VERSION}" \
    && npm cache clean --force

COPY scripts/relayforge-verifier-entrypoint.sh /usr/local/bin/relayforge-verifier-entrypoint
RUN chmod 0755 /usr/local/bin/relayforge-verifier-entrypoint

ENTRYPOINT ["/usr/local/bin/relayforge-verifier-entrypoint"]
