# Fedora Deployment And Gates

- Previous manifest: `sha256:35fc520902eb72f5ea91ececccf221883dd5fd78b1d47c78150dfd66eb04f2d3`
- Candidate manifest: `sha256:f44690e5203983e00a0d01016d65440bf1c4b83a941a490d22d4e7eea443b42a`
- Container: `1ce74be6f465ab2d334a23d3c7b08d2520ad346bd7fdb39978c76469e58356bf`
- Started: `2026-08-19T09:51:35.209256106Z`
- Status/health/restarts/OOM: running / healthy / 0 / false
- Readiness/liveliness: HTTP 200 / HTTP 200
- Recreation: only `litellm`, `--no-deps`
- Automatic rollback: not used
- Runtime projection, protected hashes, four scoped dependencies, and 46 unrelated containers: exact preflight match
- Model inventory: 27 rows, 7 default-qualified, 7 account2-qualified, 0 account3 references
- Router: 25 fallback rules, cross-profile policy enabled

LazyMCP protocol gates:

| Check | Result |
|---|---|
| HEAD | empty 204 |
| GET `*/*` | empty 204 |
| GET JSON | empty 204 |
| SSE GET | 200 SSE |
| Repeated Accept | 200 SSE |
| Quoted positive q | 200 SSE |
| q=0 | empty 204 |
| Quoted q=0 | empty 204 |
| Initialize | 200, protocol `2025-11-25` |
| Tools/list | exact `mcp_call,mcp_describe,mcp_status` |
| Status/describe/call | pass/pass/pass |

Responses/Codex gates:

| Probe | HTTP | SSE | Completed | Blocked | Exact expected selection |
|---|---:|---|---:|---:|---|
| Native account2, client `stream=false` | 200 | true | 1 | 0 | true |
| Direct account2 | 200 | true | 1 | 0 | true |
| Public fallback | 200 | true | 1 | 0 | true |

Complete candidate-window log counts were zero for standard logging/success callbacks, usage cache/cache settings, stream/response failure, auth/device flow, migration/schema/patch, LazyMCP 405/406, and generic tracebacks

Result: **PASS**
