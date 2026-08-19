# Functional Verification

## Public Native Responses

Verification window: `2026-08-19T15:41:45Z` through `2026-08-19T15:41:47Z`

| Probe | HTTP | Content-Type | Completion | Stream error | SSE error |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 200 | `text/event-stream; charset=utf-8` | yes | no | no |
| 2 | 200 | `text/event-stream; charset=utf-8` | yes | no | no |
| 3 | 200 | `text/event-stream; charset=utf-8` | yes | no | no |
| 4 | 200 | `text/event-stream; charset=utf-8` | yes | no | no |
| 5 | 200 | `text/event-stream; charset=utf-8` | yes | no | no |

During the same bounded window, staging logged zero lines, zero public-domain mentions, zero `/v1/responses` mentions, and zero `Stream must be set to true` mentions

## Compatibility and Preservation

- Public chat completion: HTTP 200 with a valid choices array
- Public readiness/liveliness: HTTP 200
- Public TLS: verify result 0, HTTP 200
- Production admin health: HTTP 200, healthy, database connected
- Production LazyMCP inventory: HTTP 200, 23 servers
- Staging readiness/liveliness: HTTP 200
- Staging authenticated model inventory: HTTP 200, 40 models
- Staging authenticated MCP inventory: HTTP 200, 23 servers
- Staging native Responses SSE: HTTP 200, completion event present, no stream error
- Production/staging: healthy, running, zero restarts, OOM false
- Fresh idle log window: production 0 tracebacks/0 stream errors; staging 0 tracebacks/0 stream errors
