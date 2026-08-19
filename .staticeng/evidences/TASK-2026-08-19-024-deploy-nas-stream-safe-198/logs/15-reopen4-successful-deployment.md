# Reopen 4 Successful NAS Deployment

## Candidate And Scope

- T0: `2026-08-19T02:09:18Z`
- Candidate manifest: `sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b`
- Candidate config/local/running image ID: `sha256:45a01917a825fa04dda4d8b0efafd1a780cfbbb9fc16d3846d654d5d49b42c73`
- Version/revision: 1.98.0 / `b0dfe2e7a7d5191871fa63224f5ed8f9544382fa`
- Container: `1fc657b5b51b7ab07b1a2ac4da13302f5e56c2123ce521481a3d82c3be36c148`
- Started: `2026-08-19T02:09:29.869606517Z`
- Mutation scope: image selector and only NAS LiteLLM recreation with `--no-deps`

## Functional Gates

- Native client `stream=false`: HTTP 200 SSE, nine valid ordered events, correct default selection, PASS
- Direct default: HTTP 200 SSE, same lifecycle and selection assertions, PASS
- Direct account2: correctly selected provider-quota HTTP 429 with no forbidden error, PASS under Tech Lead disposition
- Public `gpt-5.6-sol`: HTTP 200 SSE through default primary, PASS
- LazyMCP status/mode: enabled / `lazymcp`
- LazyMCP tools: exactly `mcp_status`, `mcp_describe`, `mcp_call`
- LazyMCP memory describe and harmless `memory-find`: PASS

## Observation And Preservation

- Observation: `2026-08-19T02:11:08Z` through `2026-08-19T02:21:13Z`
- Status/health/restarts/OOM: running / healthy / 0 / false
- Readiness/liveliness: HTTP 200 / HTTP 200
- Model/routing: 32 rows, fixed name/pair hashes, 16 fixed fallback rules
- Topology: eight default-qualified, eight account2-qualified, public default primaries with account2 fallback, zero account3 rows/references
- Credential metadata: PASS; only approved lock ctimes advanced
- Dependencies: four exact IDs, healthy, unchanged
- Mounts/networks: five / `llm-net`, `npm_npm-net`
- Wrapper/Compose hashes: `7005b7bb...7f6c` / `0a84fde5...185b`
- Config/OnePassword wrapper hashes: unchanged
- Concrete release-blocking log categories: 0

Result: **NAS PROMOTION PASS**
