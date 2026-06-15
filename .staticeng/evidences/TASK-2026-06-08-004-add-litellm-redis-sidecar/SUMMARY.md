# TASK-2026-06-08-004 Evidence Summary

## Result
Added a single Redis sidecar service to `/volume2/docker/litellm/docker-compose.yaml` and started it with Docker Compose. Redis is internal-only on `llm-net`, has no host port mapping, and requires authentication from `/volume2/docker/litellm/.env` keys `REDIS_USERNAME` and `REDIS_PASSWORD`.

## Reopen Fix
The LiteLLM dashboard connection test rejected blank username mode with `invalid username-password pair or user is disabled`. The sidecar now defines `REDIS_USERNAME=default` explicitly. A second reopen verified the actual LiteLLM `/cache/settings/test` endpoint from inside the running `litellm` container with a UI-shaped payload using `username: "default"`; it returned `Redis connection test successful`.

## LiteLLM Dashboard Cache Values
- Host: `redis`
- Port: `6379`
- Username: `default`
- Password: use the value from `/volume2/docker/litellm/.env` key `REDIS_PASSWORD` (value intentionally not recorded)
- SSL: disabled / false
- Advanced fields: leave defaults unless LiteLLM UI requires a database number; use database `0` if prompted

## Acceptance Criteria Coverage
- AC-1: Passed. `docker-compose.yaml` now includes one `redis` sidecar service using `redis:7.4-alpine`.
- AC-2: Passed. `redis-ping.log` verifies ACL username/password connectivity from the `litellm` container to hostname `redis` on port `6379`; `litellm-cache-test.log` verifies the real LiteLLM cache test endpoint succeeds with the same UI fields.
- AC-3: Passed. Redis runs as a single node service and exposes only container port `6379/tcp`, with no public host port mapping.
- AC-4: Passed. Redis username/password are sourced from `/volume2/docker/litellm/.env` keys `REDIS_USERNAME` and `REDIS_PASSWORD`; the password value is not included in evidence.
- AC-5: Passed. `docker compose up -d redis` completed after the reopen fix and `docker-compose-ps.log` shows all LiteLLM stack services running/healthy.
- AC-6: Passed. Evidence packet includes `SUMMARY.md`, `.staticeng/evidences/TASK-2026-06-08-004-add-litellm-redis-sidecar/logs/docker-compose-config.log`, `.staticeng/evidences/TASK-2026-06-08-004-add-litellm-redis-sidecar/logs/docker-compose-ps.log`, `.staticeng/evidences/TASK-2026-06-08-004-add-litellm-redis-sidecar/logs/redis-ping.log`, `.staticeng/evidences/TASK-2026-06-08-004-add-litellm-redis-sidecar/logs/litellm-cache-test.log`, and `.staticeng/evidences/TASK-2026-06-08-004-add-litellm-redis-sidecar/logs/litellm-cache-test-logs.log`.

## Verification Artifacts
- `.staticeng/evidences/TASK-2026-06-08-004-add-litellm-redis-sidecar/logs/docker-compose-config.log`: sanitized compose config validation output.
- `.staticeng/evidences/TASK-2026-06-08-004-add-litellm-redis-sidecar/logs/docker-compose-ps.log`: post-apply stack service status.
- `.staticeng/evidences/TASK-2026-06-08-004-add-litellm-redis-sidecar/logs/redis-ping.log`: Redis ACL username/password ping result from within the LiteLLM container/network.
- `.staticeng/evidences/TASK-2026-06-08-004-add-litellm-redis-sidecar/logs/litellm-cache-test.log`: Real LiteLLM `/cache/settings/test` endpoint result with secret values redacted.
- `.staticeng/evidences/TASK-2026-06-08-004-add-litellm-redis-sidecar/logs/litellm-cache-test-logs.log`: Sanitized recent LiteLLM log excerpts relevant to Redis/cache-test diagnostics.

## Notes
No UI screenshots were required because this was an infrastructure sidecar change only.
