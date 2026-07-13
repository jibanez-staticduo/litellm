# LiteLLM Error Investigation: Local/NAS and Fedora

## Decision

Both instances are healthy and all four one-shot GPT-5.6 Sol checks passed without device authorization. No DB, Redis/cache, router validation, Responses parsing, restart, health, or OOM fault was observed in either bounded window. Local/NAS has a concentrated burst of provider availability/rate-limit failures and fallback amplification; Fedora is dominated by expected bad-model client requests plus a smaller MCP-auth/cancellation pattern

The current evidence does not justify an emergency image release for Sol. Local/NAS provider/fallback behavior needs operational tuning and client attribution from sanitized structured metadata. Any future product fix or release must first replay the fork onto current `upstream/main`

## Instance Health

| Instance | Image | Started at (UTC) | Restarts | Health | Ready/live | OOM |
| --- | --- | --- | ---: | --- | --- | --- |
| Local/NAS | `staticduo-gpt-lazymcp-v1.92-replay-multiaccount-routingfix-20260711` | 2026-07-12 07:04:05 | 0 | running, healthy | 200 / 200 | no |
| Fedora | same tag | 2026-07-13 10:48:25 | 0 | running, healthy | 200 / 200 | no |

The local and Fedora image IDs differ because the release evidence records a local platform image ID and Fedora registry digest. Both run the same immutable tag, as previously documented by the release packet

## Request-Level Error Counts

Counts below come from access-log status lines, so they represent failed HTTP requests rather than repeated exception/traceback lines

| Instance/window | 400 | 404 | 429 | 500 | 503 | 507 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Local/NAS 6h | 0 | 4 | 24 | 9 | 34 | 4 |
| Local/NAS 30m | 0 | 2 | 17 | 7 | 24 | 4 |
| Fedora 6h | 19 | 0 | 0 | 0 | 0 | 0 |
| Fedora 30m | 4 | 0 | 0 | 0 | 0 | 0 |

Local 404s are OAuth discovery probes under `/lazymcp`; local 500s are eight `/lazymcp` requests plus one chat completion. The 429, 503, and 507 responses are all `/v1/chat/completions`. Fedora 400s are all `/v1/chat/completions`

## Aggregate Log Patterns

Line-pattern counts are diagnostic volume, not unique incidents. LiteLLM logs each failed request through multiple nested exception and fallback frames

| Instance/window | Lines | ERROR | WARNING | Traceback | Rate limit | Fallback | Cancel | Timeout |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Local/NAS 6h | 35,964 | 1,425 | 12 | 614 | 120 | 1,932 | 6 | 0 |
| Local/NAS 30m | 25,783 | 1,196 | 12 | 514 | 115 | 1,622 | 6 | 0 |
| Fedora 6h | 2,905 | 108 | 9 | 88 | 0 | 0 | 12 | 18 |
| Fedora 30m | 606 | 32 | 3 | 30 | 0 | 0 | 4 | 6 |

Zero matches in both windows: router/profile validation, DB exception, Redis/cache exception, Responses parsing error, and OOM. No `Unknown items in responses API response` recurrence was found

## Root Causes

### Local/NAS

1. **Transient provider availability and quota pressure, amplified by fallback/retry logging.** There were 34 HTTP 503 and 24 HTTP 429 chat failures in 6h; 24 and 17 respectively occurred in only 30m. Exception-line volume is dominated by `ServiceUnavailableError` (1,234), `ChatgptException` (476), and `RouterRateLimitError` (96). The dominant affected groups in exception-bearing lines were `chatgpt/gpt-5.5`, `chatgpt/gpt-5.4-mini`, and regular Sol. Account2 Sol was much less represented. Repeated traceback/fallback frames explain why exception mentions greatly exceed failed requests
2. **Fallback exhaustion rather than a proven fallback loop.** The parser found 468 no-fallback/exhaustion mentions, but no loop/cycle/max-fallback marker. Regular Sol had 84 rate-limit and 168 service-unavailable exception-line co-mentions; account2 Sol had 12 each. Current bidirectional profile fallback can exhaust both profiles during a shared provider cooldown. This is transient/provider plus router policy behavior, not evidence of profile leakage or recursive looping
3. **Expected/operational auth and client noise.** `KeyNotFoundError` appeared 64 times and six cancellations were logged. These are separate from Sol and do not indicate DB loss. Eight LazyMCP 500 requests and four discovery-route 404s are an MCP/client compatibility issue. Four chat 507s and one chat 500 need sanitized request metadata correlation before assigning a code root cause

### Fedora

1. **Expected client model errors.** All 19 failed requests were HTTP 400. `ProxyModelNotFoundError` dominated exception classes (76 repeated log mentions), with no fallback activity and no Sol error-line association. This points to clients requesting an unavailable/invalid model rather than provider or infrastructure failure
2. **MCP upstream auth and disconnect/timeout noise.** `MCPUpstreamAuthError` appeared 12 times, cancellations 12 times, and timeout-pattern lines 18 times. These patterns are not associated with Sol and did not affect health. They should be fixed at the calling client/MCP authorization layer unless sanitized structured metadata proves a proxy mapping bug
3. **No provider quota burst or profile/device issue.** No 429, 5xx, fallback, device-code marker, Responses parsing error, DB/cache error, restart, or OOM indicator was observed

## GPT-5.6 Sol Contract

Exactly one request per current model was sent on each instance, with no manual retry. Only HTTP status and harmless sentinel match were retained

| Instance | Public model | Requests | HTTP | Sentinel | Device auth |
| --- | --- | ---: | ---: | --- | --- |
| Local/NAS | `chatgpt/gpt-5.6-sol` | 1 | 200 | pass | none |
| Local/NAS | `chatgpt-account2/gpt-5.6-sol` | 1 | 200 | pass | none |
| Fedora | `chatgpt/gpt-5.6-sol` | 1 | 200 | pass | none |
| Fedora | `chatgpt-account2/gpt-5.6-sol` | 1 | 200 | pass | none |

Current status: regular and account2 Sol are operational on both instances. Historical Fedora evidence from 2026-07-13 showed regular Sol transiently rate-limited while account2 passed; the present one-shot checks show both recovered

## Upstream and Release Decision

Read-only `git fetch upstream main` advanced `upstream/main` to `10d5804b3ef4`; the fork worktree is at `960e343ef297` and is not an ancestor of current upstream. Upstream includes newer Responses work such as `249a999506` (in-stream error events) and `2f0cdb35bf` (Responses bridge/tool round-trip), but neither matches an observed current parsing failure. No current upstream commit was found that clearly resolves the local provider cooldown/fallback burst

An upstream sync/new image is **not required to restore current Sol service**. It **is required before any later code/image fix**, following the task's replay strategy. Do not sync merely to address transient provider quota or invalid client model requests

## Actionable Fix Plan

1. Identify the local clients behind the 34/24 provider failures and Fedora clients behind the 19 invalid-model requests using only time bucket, requested model/group, provider, exception class, status, and fallback outcome. Do not retain client identity or request content
2. Review local retry, cooldown, and bidirectional cross-profile fallback policy so one provider quota event does not produce a large traceback/fallback fan-out. Preserve bounded retries and prevent revisiting attempted groups
3. Correct Fedora client model catalogs/defaults that issue unavailable model names; this is a client/config fix and does not need a LiteLLM image
4. Validate the local 507 and LazyMCP 500 classes separately with sanitized structured metadata. Escalate to code only if reproducible with a minimal payload and not caused by caller auth/disconnect behavior
5. If a reproducible Responses bridge or fallback state bug remains after attribution, replay onto `upstream/main`, reconcile the existing multiaccount patch with current router code, add focused regression tests, build one immutable image, and deploy both instances through separate release tasks

## Evidence Safety and Method

Only aggregate counts, model-group names, exception classes, HTTP statuses, container metadata, and sentinel booleans are stored. No raw container logs, DB rows, prompts, response bodies, identities, IPs, keys, tokens, headers, account IDs, auth contents, device codes, DB URLs, or request/session IDs are present

Machine-readable aggregate evidence is in `aggregate.json`
