# Production and Dependency Verification

## Public production behavior

| Check | Result |
|---|---|
| Readiness | HTTP 200 |
| Liveliness | HTTP 200 |
| TLS | verification result 0 |
| Codex-compatible Responses | HTTP 200, `text/event-stream`, one completion, no stream-required or SSE error |
| Chat completion | HTTP 200, JSON choices present, no error object |
| LazyMCP status | enabled, 23 servers, 488 tools |
| LazyMCP describe | pass |
| LazyMCP harmless memory health call | pass; all configured backends healthy |

Authorization values, prompts, response content, and response identifiers were not retained

## Routing and preservation

- Public DNS resolved `litellm.staticduo.com` to the established NAS address
- NPM resolved `litellm-production` to only production `172.28.0.29`
- NPM host 62 retained SHA-256 `614887a180eec00c09d78cd2b22df668cd093246748ac726638f15a80e209053` and target `http://litellm-production:4000`
- NPM Nginx syntax passed and TLS remained enabled
- Production retained container `3d92b5aa1f96...`, start time `2026-08-19T15:38:30Z`, healthy running state, zero restarts, and OOM false
- Staging PostgreSQL, staging Redis, production Redis, both LiteLLM admin MCP services, and NPM retained their identities/start times and healthy running state
- Post-stop log classification found zero traceback, stream-required, OOM, emerg, critical, or panic patterns across production, NPM, staging PostgreSQL, and staging Redis
- Fedora, tags, production configuration, NPM configuration, and unrelated services were not mutated
