# LiteLLM Operational Error Fix

## Decision

The actionable configuration issues were corrected without app-code or image changes. Fedora stale Hermes and OpenClaw catalog entries were removed, and NAS DB-backed retries were reduced from three to one to bound provider-error amplification. The NAS 507 responses were upstream ChatGPT capacity/storage responses, not a LiteLLM budget or client quota policy. LazyMCP 500 responses were invalid caller-key failures before MCP dispatch; the current OpenCode LazyMCP configuration and gateway discovery are healthy, so no registry or credential mutation was appropriate

No reproducible code defect remains. No upstream replay or release is recommended

## Exact Changes

| Scope | Configuration | Change |
| --- | --- | --- |
| Fedora | `/home/staticduo/.hermes/config.yaml` | Removed 8 catalog entries absent from live Fedora LiteLLM |
| Fedora | `/home/staticduo/.openclaw/openclaw.json` | Removed 5 catalog entries absent from live Fedora LiteLLM |
| NAS | PostgreSQL `LiteLLM_Config` `router_settings` | Changed `num_retries` from 3 to 1 |

Defaults, fallbacks, model deployments, model contents, and credentials were preserved. Fedora OpenCode required no change because its defaults and plugin overrides resolve to live models. NAS retained all 8 fallback rules. Fedora retained all 19 fallback rules, including every explicit bidirectional regular/account2 pair

## Backups

- Fedora Hermes: `/home/staticduo/.hermes/config.yaml.bak-operational-errors-20260713T222745Z`
- Fedora OpenClaw: `/home/staticduo/.openclaw/openclaw.json.bak-operational-errors-20260713T222745Z`
- NAS router settings: `/volume2/docker/litellm/data/router_settings.bak-operational-errors-20260713T222807Z.json`

All backups are mode `0600` and contain no material copied into this evidence packet

## Attribution

Fedora invalid requests named `qwen3` and `deepseek_v4_flash`. Sanitized proxy logs did not carry a safe application marker, so their source category is recorded as other/unattributed rather than inferring an identity. Both names were unavailable, and the known local client catalogs also contained stale server names; catalog cleanup prevents selection of those stale entries under our control

NAS chat 507 was the provider's `Insufficient Storage` response from the ChatGPT Responses route, surfaced as `ChatgptException`. No LiteLLM budget, spend-limit, quota, or client-limit exception was present, so no policy was changed

NAS LazyMCP 500 occurred during proxy-key authentication/context preparation as `KeyNotFoundError`; requests did not reach MCP initialize, tool listing, tool calls, or an upstream server. The current OpenCode client carries configured auth headers, and a post-change LazyMCP status call succeeded with 24 servers and 535 tools. Historical callers with stale keys must refresh their client credential; credentials were intentionally not inspected or changed

## Retry And Fallback Control

NAS `num_retries=3` amplified provider 429/503/507 failures before fallback processing. It was reduced to one bounded retry. `allowed_fails=1`, `cooldown_time=30`, retry policy defaults, and all fallback rules were preserved. The direct DB update required one explicit LiteLLM restart because the running router did not hot-load the value; health returned healthy and live settings confirmed `num_retries=1`

Fedora settings were already bounded enough for its observed client errors and had no retry/fallback fan-out, so no Fedora router change was made

## Post-Change Measurement

Existing traffic was present, so no extra Sol smoke requests were sent. In the bounded 30-minute post-change measurement, Fedora had no unavailable-model errors, while NAS had no 507 or LazyMCP 500. NAS continued to receive seven 429 and seven 503 chat failures from provider availability/rate-limit pressure; these remain unavoidable provider conditions, now with fewer configured retries. Fedora had twelve separate 403 caller-authorization responses outside this task's invalid-model scope

Regular and account2 Sol were already proven operational on both instances by the parent evidence. Neither model deployment nor its fallback pair was changed in this task

## Validation

- Hermes and OpenClaw structured config validation passed
- Fedora Hermes and OpenClaw gateways are active after restart
- Fedora client catalogs now have zero entries absent from the live server inventory
- NAS LiteLLM is running and healthy after restart
- Live NAS router settings report one retry, one allowed failure, 30-second cooldown, and all 8 prior fallbacks
- Current LazyMCP status succeeds
- No source code, image, credentials, model deployments, model contents, or MCP registry rows changed

## Remaining Causes

- Provider availability and rate limiting still produce NAS 429/503 failures
- Historical LazyMCP clients using revoked or stale credentials can still fail until those callers refresh their own configured key
- Fedora caller authorization 403 responses remain separate operational noise

None is a reproducible LiteLLM code defect in this evidence window

## Evidence Safety

This packet contains only model aliases, application categories, routes, status counts, exception classes, bounded router values, backup paths, and validation outcomes. It contains no prompts, responses, users, IPs, keys, tokens, headers, IDs, auth/device details, database URLs, or raw logs
