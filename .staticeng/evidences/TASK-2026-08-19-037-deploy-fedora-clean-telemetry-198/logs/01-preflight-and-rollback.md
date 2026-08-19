# Fedora Fresh Preflight And Rollback

- Captured: `2026-08-19T04:03:39Z`
- Running selector and manifest: `sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b`
- Container: `b4cff1ee704ccf7c...` started `2026-08-19T02:32:15.989297648Z`
- Status/health/restarts/OOM: running / healthy / 0 / false
- Readiness/liveliness: HTTP 200 / HTTP 200
- Mounts/networks: 5 / `llm-net`, `npm_npm-net`
- Running containers: 47
- Unrelated-container projection: `f254639a36f36223b9904bcd1d734461b0985280e4f9c2cfaa993092ca974a56`
- Model rows/projection: 27 / `b3711553b92b632e66520c133c5876e0799a06ede12850c7ed9a056bbc24b49b`
- Router projection/fallback count/cross-profile policy: `2d1d6f99755445930c8a1aabda00ca9fefe576a2419656c8dc25b992d103dc5f` / 24 / true
- Protected Compose/config/wrapper/OnePassword-wrapper hashes: `af1a6462...d6`, `f3b83ce7...67`, `9e9b0de7...6e`, `31f719b7...89`
- Non-image environment projection: `4e1eeae3033e183adb6b5a00ef06f2a3b05257f5f30f57b7a7be69bcef1355bc`
- Five-file credential metadata projection: `98b44ba08c7158b2254764353a6b32234ce7ea8cf0398bd463baef2eff5d4c11`
- PostgreSQL, Redis, admin MCP, and compatibility MCP were running and healthy
- Candidate and rollback were pulled and resolved before mutation
- Candidate identity: manifest `sha256:35fc5209...f2d3`, version 1.98.0, revision `177c66ef727710a455f058b99f653df9b3e4c0a4`, amd64
- Rollback identity: manifest `sha256:42d36549...115b`, version 1.98.0, revision `b0dfe2e7a7d5191871fa63224f5ed8f9544382fa`, amd64
- Protected rollback directory: `/home/staticduo/docker/litellm/releases/20260819-clean-telemetry-198/20260819T040414Z`

Result: **PASS**
