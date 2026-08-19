# NAS Deployment And Gates

- Previous manifest: `sha256:35fc520902eb72f5ea91ececccf221883dd5fd78b1d47c78150dfd66eb04f2d3`
- Candidate manifest: `sha256:f44690e5203983e00a0d01016d65440bf1c4b83a941a490d22d4e7eea443b42a`
- Config digest/image ID: `sha256:84dd79e310f6c5804c50e304fb36479ed6c019ffbff6a64b5b5c91b6b4c4ceed`
- Container: `122510897d181c943e6c2dbaa6113a168e249fd882bc60a4f916617a32c65c30`
- Started: `2026-08-19T09:55:49.867042351Z`
- Status/health/restarts/OOM: running / healthy / 0 / false
- Readiness/liveliness: HTTP 200 / HTTP 200
- Recreation: only `litellm`, `--no-deps`
- Automatic rollback: not used
- Runtime projection, protected hashes, four scoped dependencies, and 142 unrelated containers: exact preflight match
- Model inventory: 32 rows, 8 default-qualified, 8 account2-qualified, 0 account3 references
- Router: 16 fallback rules, cross-profile policy enabled

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
| Native default, client `stream=false` | 200 | true | 1 | 0 | true |
| Direct default | 200 | true | 1 | 0 | true |
| Direct account2 | 200 | true | 1 | 0 | true |
| Public default-primary | 200 | true | 1 | 0 | true |

Complete candidate-window log counts were zero for standard logging/success callbacks, usage cache/cache settings, stream/response failure, auth/device flow, migration/schema/patch, LazyMCP 405/406, and generic tracebacks

Result: **PASS**
