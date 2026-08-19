# Functional Verification

## Public routing and clients

- TLS verification: OK, return code 0
- Public readiness: HTTP 200
- Public liveliness: HTTP 200
- NPM DNS for `litellm-production`: one address, production `172.28.0.29`
- Corrected Codex probe shape: public `gpt-5.6-sol`, list-form input, `reasoning.context=all_turns`, native streaming, no client retry, stateless request, encrypted reasoning inclusion, Codex Responses Lite header

| Probe | HTTP | Content type | Completion | Stream error | SSE error |
|---|---:|---|---|---|---|
| Codex 1 | 200 | `text/event-stream` | yes | no | no |
| Codex 2 | 200 | `text/event-stream` | yes | no | no |
| Codex 3 | 200 | `text/event-stream` | yes | no | no |
| Chat | 200 | `application/json` | choices present | no | no |

Request and response contents and authorization values were not retained

## Health and preservation

- Staging loopback readiness and liveliness: HTTP 200
- LiteLLM admin health: HTTP 200, status healthy, database connected
- LiteLLM admin inventory: 23 MCP servers and 32 models
- LazyMCP: enabled, 23 visible servers, 488 visible tools; status/describe/call paths remained functional
- Production, staging, Redis dependencies, staging PostgreSQL, both admin MCP services, and NPM retained their pre-task start times
- All checked containers remained running and healthy with zero restarts and OOM false
- NPM configuration syntax passed
- Final bounded post-success logs: zero traceback, stream-required, OOM, emerg, or critical matches for production, staging, and NPM

## Non-impact notes

- No container or service was restarted or recreated
- The targeted no-op NPM API update regenerated/reloaded only host 62
- Two initial malformed model-selection probes returned HTTP 400 before the corrected probes; no service fault occurred and the final bounded log window was clean
