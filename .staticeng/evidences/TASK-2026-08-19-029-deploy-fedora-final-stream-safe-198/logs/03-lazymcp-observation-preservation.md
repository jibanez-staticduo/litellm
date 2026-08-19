# LazyMCP, Observation, And Preservation

## LazyMCP

- Protocol: `2025-11-25`
- Gateway tools: exactly `mcp_status`, `mcp_describe`, `mcp_call`
- `mcp_status`: PASS
- `mcp_describe` for Fedora's `defend_memory-find`: PASS
- Harmless `mcp_call` to `defend_memory-find`: PASS

Fedora exposes the memory server as `defend_memory`; its described tool is `defend_memory-find`. Earlier probe assumptions using NAS's `memory` alias and unprefixed tool name were diagnostic harness errors, not LazyMCP failures

## Ten-Minute Observation

- Candidate start: `2026-08-19T02:32:15.989297648Z`
- Final observation check: `2026-08-19T02:42:26Z`
- Container identity/start time: unchanged
- Status/health/restarts/OOM: running / healthy / 0 / false
- Readiness/liveliness: HTTP 200 / HTTP 200

## Preservation

- `.env`: exactly one image selector; all non-image content matches protected rollback backup
- Compose/config/wrapper/OnePassword wrapper hashes: exact preflight match
- Public/deployment/fallback counts: 27 / 27 / 24
- Public/deployment/router projections: exact preflight match
- Two-account topology: seven default-qualified and seven account2-qualified deployments, cross-profile policy preserved
- Credential metadata: all five records exact; credential contents were never read
- Dependency identities/health: exact and healthy
- Running containers/mounts/networks: 47 / 5 / two exact networks

## Sanitized Candidate Log Categories

- `Stream must be set to true`: 0
- Authentication required: 0
- Device flow: 0
- Migration failed: 0
- Schema error: 0
- Patch failed: 0
- `response.failed`: 0
- Unsupported value/model: 0
- Generic traceback lines: 2

The two tracebacks are non-blocking success-telemetry callback errors: one cost callback and one Prometheus success logger reported a missing standard logging object after an HTTP 200 response. They are disclosed for audit and are not concrete stream, request, auth, device, migration, schema, patch, health, restart, or OOM failures

Result: **LAZYMCP, OBSERVATION, PRESERVATION, AND CONCRETE CLEAN-LOG GATES PASS**
