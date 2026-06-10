---
task_id: TASK-2026-06-08-004-add-litellm-redis-sidecar
complexity: standard
track: implementation
slice: core
status: done
assigned_to: developer
handoff_from: product_manager
scr: none
parent: none
---

# Add LiteLLM Redis Sidecar

## Context
The LiteLLM Docker stack lives at `/volume2/docker/litellm`. The user wants Redis available as a node/single-instance cache backend for the LiteLLM dashboard caching settings. Add Redis as a sidecar service in the existing `docker-compose.yaml` if it is not already present.

Current known stack details:
- Compose file: `/volume2/docker/litellm/docker-compose.yaml`
- Env file: `/volume2/docker/litellm/.env`
- Existing networks: external `llm-net`, external `npm_npm-net`
- LiteLLM service talks internally on port `4000`
- Existing compose services at task start: `litellm`, `litellm-admin-mcp`, `litellm-admin-mcp-compat`

## Classification
- complexity: standard
- track: implementation
- slice: core
- SCR: not required; infrastructure sidecar only, no product specification change

## Acceptance Criteria
- AC-1: `docker-compose.yaml` includes one Redis sidecar service for the LiteLLM stack, unless an equivalent service already exists.
- AC-2: Redis is reachable by the LiteLLM container on the Docker network using a stable hostname suitable for the dashboard Host field.
- AC-3: Redis is configured as a single node instance and does not expose unnecessary public host ports.
- AC-4: Redis authentication details are clear. If a password is used, store it via `.env` and report the env key only, not the secret value.
- AC-5: The stack is applied safely and `docker compose ps` shows the resulting services healthy/running.
- AC-6: Evidence is written under `.staticeng/evidences/TASK-2026-06-08-004-add-litellm-redis-sidecar/` with `SUMMARY.md` and logs.

## Constraints
- Do not print secrets in the final response or evidence.
- Do not modify unrelated dirty files under `/volume2/docker`.
- Preserve existing LiteLLM image, MCP services, and networks.
- Prefer no host port mapping for Redis.
- If choosing an image, use an official Redis/Valkey-compatible image with a stable tag; keep the compose change minimal.

## Expected Evidence
- `logs/docker-compose-config.log`: sanitized `docker compose config` or equivalent validation output.
- `logs/docker-compose-ps.log`: post-apply service status.
- `logs/redis-ping.log`: Redis ping from within the stack without exposing password value.
- `SUMMARY.md`: state exact UI field values for Host, Port, Username, Password source, SSL, and any advanced fields.

## Handoff
[Agent Message] From: product_manager To: developer
Please implement this task exactly as scoped. Inspect the current compose and env, add Redis sidecar only if missing, apply the stack safely, verify reachability from the LiteLLM network, and create the evidence packet. In your handoff back, include the exact LiteLLM dashboard fields the user should enter, but do not reveal password values; reference the env var/file location instead.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

Implemented the Redis sidecar in `/volume2/docker/litellm/docker-compose.yaml` as service `redis` using `redis:7.4-alpine`, attached only to external network `llm-net`, with no host port mapping. Added `/volume2/docker/litellm/.env` key `REDIS_PASSWORD` and used it for Redis authentication without recording the secret value.

Applied the change with `docker compose up -d redis`. Verification evidence is stored under `.staticeng/evidences/TASK-2026-06-08-004-add-litellm-redis-sidecar/` and includes sanitized compose config, post-apply `docker compose ps`, Redis ping from the `litellm` container to `redis:6379`, and AC coverage summary.

Expected LiteLLM cache UI values after reopen fix: Host `redis`, Port `6379`, Username `default`, Password from `/volume2/docker/litellm/.env` key `REDIS_PASSWORD`, SSL disabled, advanced fields left at defaults unless the UI asks for DB number `0`.

# Reopen History

## 2026-06-08: LiteLLM UI rejects blank username

The user reported LiteLLM dashboard test connection error: `invalid username-password pair or user is disabled` after saving Redis settings with host `redis`, port `6379`, username blank, and password populated. Reopen scope: determine whether LiteLLM/redis client requires explicit ACL username for Redis 6+ and update Redis sidecar/auth/UI guidance accordingly without exposing the password value.

## 2026-06-08: LiteLLM UI still rejects username default

The user reported the same error after entering username `default`. Reopen scope: inspect LiteLLM's actual cache test implementation/logs and determine whether the UI/API expects Redis username omitted, `None`, disabled, URL format, or a different auth shape. Fix the stack or provide confirmed UI values only after verifying against the real LiteLLM endpoint, not only raw Redis CLI.

Resolution: configured explicit `REDIS_USERNAME=default` in `/volume2/docker/litellm/.env`, updated the Redis sidecar healthcheck to authenticate with `--user "$REDIS_USERNAME" --pass "$REDIS_PASSWORD"`, recreated the Redis sidecar, and refreshed evidence. Verification now uses ACL-style `AUTH <username> <password>` from the `litellm` container and returns `PONG`. Corrected UI fields require Username `default`.

Follow-up verification: inspected LiteLLM cache settings code and confirmed the UI posts to `/cache/settings/test` with `cache_settings` gathered from the visible fields. The backend creates `Cache(**cache_settings)`, passes `username` through to `RedisCache.redis_kwargs`, and `test_connection()` calls `redis.asyncio.Redis(**self.redis_kwargs).ping()`. Verified the real running LiteLLM endpoint from inside the `litellm` container with payload shape `{type: redis, host: redis, port: "6379", username: default, password: <redacted>}`; it returned `Redis connection test successful`. Added `logs/litellm-cache-test.log` and sanitized log excerpts.
