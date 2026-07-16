# Fedora LiteLLM Routing Error Investigation

## Decision

Fedora reproduces the ChatGPT authentication/cooldown and invalid-model classes, but the inspected 36-hour window does not reproduce a context-window overflow. The running service is healthy, has no restarts or OOM, and uses the expected immutable multi-account routing image

The dominant current client fault is a stale OpenCode catalog entry for `qwen3.6-35b-a3b-uncensored-nvfp4`. It is requested continuously, but is absent from both LiteLLM's 19-model runtime inventory and the configured deployment list. The valid nearby deployed name is `qwen3.6-27b-aeon-ultimate-uncensored-multimodal-nvfp4-mtp`

## Findings

### 1. ChatGPT 401 and cooldown exhaustion: reproduced

- Two `/v1/chat/completions` requests returned HTTP 401 at `2026-07-15T04:54:57Z` and `2026-07-15T04:55:19Z`
- Sanitized exception correlation shows repeated `ChatgptException` 401 lines later co-occurring with cooldown/fallback exhaustion and `RouterRateLimitError`
- Fedora router config sets `num_retries: 3`, `allowed_fails: 1`, and `cooldown_time: 30`
- With explicit `allowed_fails`, LiteLLM uses one failure counter per deployment. The first failure increments the counter; the next failure within the 30-second TTL cools the deployment, regardless of exception class
- General bidirectional ChatGPT profile fallbacks are database-backed. When both paired profiles fail or are cooled, the router exhausts available deployments and returns HTTP 429. The window contains 107 chat 429 responses and 1,560 repeated exhaustion-pattern lines

Immediate cause: upstream ChatGPT authentication rejection, followed by deployment cooldown and exhaustion of configured fallback candidates

Underlying cause: invalid or expired ChatGPT authentication state for at least one selected deployment, amplified by the global `allowed_fails: 1` policy and cross-profile fallback fan-out. Logs do not safely identify an account profile, so the affected profile must be established with secret-safe per-deployment health/auth checks before reauthentication

### 2. Context-window overflow: not reproduced; cooldown interaction is explainable

- No `ContextWindowExceededError`, context-length, context-window, maximum-context, or too-many-tokens marker appears in the bounded 36-hour Fedora logs
- Fedora's file-backed router settings do not define `context_window_fallbacks`; the prior database-backed fallback evidence documents general profile fallbacks only
- LiteLLM routes `ContextWindowExceededError` through `context_window_fallbacks` when configured; otherwise it falls through to general fallbacks
- Cooldown accounting is independent from fallback selection. With `allowed_fails: 1`, a prior 401 and a subsequent context error on the same deployment inside 30 seconds can legitimately cross the shared failure threshold and cool it. This is expected under the configured generic policy, although a prompt-size error is request-specific and cooling a healthy deployment for it is operationally undesirable

Immediate cause in the supplied sequence, if its context event belongs to Fedora: the request exceeds the selected model's accepted input limit and no dedicated context fallback exists

Underlying cause: missing context-specific fallback policy plus exception-agnostic low failure threshold. Current Fedora logs do not independently prove that supplied context event occurred here

### 3. Invalid requested Qwen alias: reproduced continuously

- The invalid alias has 9,264 repeated log-line mentions and drives `ProxyModelNotFoundError`; 2,316 chat requests returned HTTP 400 in the window
- Runtime `/model/info` contains 19 model groups and does not contain the alias
- Fedora `~/.config/opencode/opencode.json` catalogs both the nonexistent alias and the valid deployed Qwen alias
- OpenCode defaults remain ChatGPT models, so the stale alias is likely selected by an agent/job/model override rather than the global default

Immediate cause: the client requests a public model name absent from LiteLLM

Underlying cause: client catalog drift. No server alias or deployment maps `qwen3.6-35b-a3b-uncensored-nvfp4`

## Exact Repair Surfaces

1. Fedora ChatGPT auth material under the mounted `/app/data/chatgpt-auth` path, using the existing supported auth workflow for only the profile proven unhealthy. Do not edit token files directly
2. Fedora database-backed model definitions for the affected `chatgpt/*` or `chatgpt-account2/*` deployment only if health inspection shows a wrong profile association; otherwise leave model rows unchanged
3. Fedora database-backed `router_settings` record in `LiteLLM_Config`, managed through `POST /fallback` where supported, for dedicated `context_window_fallbacks` and any deliberate fallback-policy adjustment
4. Fedora `/home/staticduo/docker/litellm/config.yaml` for `allowed_fails`, `cooldown_time`, and retry policy. Avoid changing these until auth is repaired and a focused policy test defines desired context-error behavior
5. Fedora `~/.config/opencode/opencode.json` override catalog: remove or rename `qwen3.6-35b-a3b-uncensored-nvfp4` to the intended existing model. Search agent/job overrides for the same literal before validation

The repository root `docker-compose.yml` and `proxy_server_config.yaml` are upstream development examples, not the live Fedora deployment. The live stack is `/home/staticduo/docker/litellm/docker-compose.yaml` with read-only `/app/config.yaml` and persistent `/app/data` mounts

## Minimal Repair and Verification Plan

1. Stop the client/job repeatedly requesting the nonexistent Qwen name, then correct only its Fedora OpenCode catalog/override to the intended existing runtime model
2. Run secret-safe health checks for each paired ChatGPT deployment and reauthenticate only the profile returning 401 through the supported OAuth/auth command. Do not rotate unrelated profiles
3. Verify one minimal request to each repaired ChatGPT primary and counterpart; retain only model group, status, selected profile label, and fallback outcome
4. Add explicit context-window fallbacks only where the target has a demonstrably larger accepted context. Do not reuse the ordinary same-provider account counterpart as a context fallback when it has the same limit
5. Before changing cooldown policy, add a focused regression test proving a request-specific `ContextWindowExceededError` does not poison an otherwise healthy deployment, while 401/429 behavior remains bounded. If a config-only solution cannot express this, use a separate implementation task
6. Verify the stale Qwen literal produces zero new log entries, the corrected model returns a non-model-not-found result, ChatGPT 401 stops, and fallback/cooldown 429 volume returns to baseline

## Evidence Safety

Evidence stores only timestamps, aggregate counts, public model-group names, exception classes, HTTP statuses, non-secret container metadata, and sanitized configuration keys. No prompts, responses, identities, IPs, request/session IDs, headers, credentials, account IDs, auth files, token values, DB URLs, or full config/environment files are included

## Evidence Files

- `.staticeng/evidences/TASK-2026-07-16-001-investigate-fedora-litellm-routing-errors/logs/container-and-deployment-sanitized.log`
- `.staticeng/evidences/TASK-2026-07-16-001-investigate-fedora-litellm-routing-errors/logs/recent-routing-aggregate-sanitized.json`
- `.staticeng/evidences/TASK-2026-07-16-001-investigate-fedora-litellm-routing-errors/logs/model-and-client-inventory-sanitized.json`
- `.staticeng/evidences/TASK-2026-07-16-001-investigate-fedora-litellm-routing-errors/logs/code-paths-sanitized.log`
