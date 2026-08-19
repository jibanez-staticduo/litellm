# NAS LiteLLM Upstream Collision Fix

## Summary

Removed staging from the public proxy network, assigned production the unique `litellm-production` alias, repointed NPM host 62 to that alias, and upgraded staging to the current stable stream-safe manifest without rollback

## Work Performed

- Captured sanitized pre-change Compose, image, network, DNS, NPM, health, and runtime identity baselines
- Created an owner-only backup at `/volume2/docker/litellm/releases/20260819T153656Z-TASK-2026-08-19-056-upstream-collision`
- Added `litellm-production` only to production on `npm_npm-net`
- Removed staging from `npm_npm-net` while preserving its private staging network, `llm-net`, loopback port, mounts, database, Redis, and configuration
- Upgraded staging to stable manifest `sha256:f44690e5203983e00a0d01016d65440bf1c4b83a941a490d22d4e7eea443b42a`, revision `8589869e1c745ae5c66d96e5475aa816496bc060`
- Recreated only the production and staging LiteLLM services with `--no-deps`
- Updated NPM host 62 through the NPM API to `http://litellm-production:4000`
- Ran public, staging, NPM, TLS, DNS, LazyMCP, dependency-preservation, stream, and clean-log verification

## Acceptance Criteria Coverage

- **AC-1: PASS**. Pre-change evidence captured the two-IP `litellm` resolution, aliases, NPM host 62 upstream, production/staging image revisions, healthy status, restart/OOM state, Compose hashes, and rollback files
- **AC-2: PASS**. `litellm-production` resolves from NPM to exactly production `172.28.0.29`; NPM host 62 exclusively targets `litellm-production:4000`
- **AC-3: PASS**. Staging no longer joins `npm_npm-net` and now runs the exact stable manifest, LiteLLM 1.98.0, revision `8589869e1c`
- **AC-4: PASS**. Five bounded public native Responses requests reached production with HTTP 200 while the staging log window remained empty with zero `/v1/responses`, public-domain, or stream-error mentions
- **AC-5: PASS**. All five public probes returned `text/event-stream`, emitted completion events, and contained neither SSE errors nor `Stream must be set to true`; public chat returned HTTP 200 and LazyMCP retained 23 servers
- **AC-6: PASS**. Production and staging are healthy with zero restarts/OOM. Production retained five mounts, staging retained six, all five checked dependencies retained identity/start time, NPM is online, Nginx syntax passes, TLS verifies, and bounded idle logs are clean
- **AC-7: PASS**. This packet records the durable network topology and validation results. No product behavior, application source, architecture, or CodeMap update is required

## Documentation Impact

The durable operational topology is now: NPM host 62 -> `litellm-production:4000` on `npm_npm-net`; staging is private to `litellm-staging` plus shared internal `llm-net` and remains loopback-accessible at `127.0.0.1:14000`. This evidence packet is the runbook record. The older staging design document describes the original temporary topology and was not changed because this task operated only on NAS deployment files outside the repository

## Open Risks

- Production still has the generic `litellm` alias because Compose derives it from the production service name; it resolves only to production and NPM no longer uses it
- The pre-change production Compose and generated NPM file were world-writable. Production Compose is now mode 0600, while NPM regenerated host 62 as mode 0777 according to its existing runtime behavior; the owner-only backup remains mode 0600
- Earlier failed validation probes intentionally generated malformed-input and invalid-key tracebacks. A fresh bounded idle window had zero tracebacks and zero stream errors on both services
- `staticeng_validate` remains blocked by inherited broken `.staticeng/codemap.yml` links and repository-wide missing CodeMaps. The required repair dry-run proposes broad unrelated changes, so it was not applied

## Recommended Next Step

PMA should route this packet for independent QA and closure
