# Current State And Preservation

## Fedora

- Container: `43ca1ba9c48916f748c0e23e4366603e0abcfde20c5c8686c9028e510cae5941`
- Manifest: `sha256:35fc520902eb72f5ea91ececccf221883dd5fd78b1d47c78150dfd66eb04f2d3`
- Registry config: `sha256:9975f878bd5080e95ba6df47f36422b291bcf2123f32b00a81e69ca5bf7c9a3a`
- Status/health/restarts/OOM: running / healthy / 0 / false
- Readiness/liveliness: HTTP 200 / HTTP 200
- Topology: 27 models / 24 fallback rules / 7 default-qualified / 7 account2-qualified / 0 account3 references
- Dependencies: PostgreSQL, Redis, admin MCP, and compatibility MCP exact and healthy
- Runtime: 5 mounts / `llm-net`, `npm_npm-net` / 47 running containers
- Credential metadata/path set: unchanged, zero lock ctime advances
- Protected Compose/config/startup/OnePassword wrapper and non-image environment projections: unchanged
- LazyMCP protocol/tool list/status/describe: PASS
- Observation: 8,084 seconds from candidate start, zero release-blocking categories, four generic traceback audit hits
- Rollback manifest `sha256:42d36549...115b`: locally resolvable linux/amd64 with matching non-image environment

The functional matrix is sourced from the prior live deployment gates and cryptographically anchored to their sanitized source summaries. The current container ID and start time are unchanged, so no new provider request was sent and credential bytes remained untouched

## NAS And Stable

- NAS container: `5933659e6a1480b6c25500389b018d44881ccd5a4797df2feb0d3c1f68107fab`
- NAS status/health/restarts/OOM: running / healthy / 0 / false
- NAS manifest: same replacement digest as Fedora
- NAS before/after identity: exact
- Stable before/after: `MISSING_OR_UNRESOLVED`, unchanged

Result: **PASS**
