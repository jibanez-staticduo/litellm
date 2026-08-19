# Fedora Deployment And Identity

- Changed only Fedora `LITELLM_IMAGE`
- Pulled the immutable candidate and recreated only `litellm` with `docker compose ... up -d --no-deps litellm`
- Candidate manifest: `sha256:35fc520902eb72f5ea91ececccf221883dd5fd78b1d47c78150dfd66eb04f2d3`
- Registry config digest: `sha256:9975f878bd5080e95ba6df47f36422b291bcf2123f32b00a81e69ca5bf7c9a3a`
- Platform/version/revision: linux/amd64 / 1.98.0 / `177c66ef727710a455f058b99f653df9b3e4c0a4`
- Final container: `43ca1ba9c48916f748c0e23e4366603e0abcfde20c5c8686c9028e510cae5941`
- Started: `2026-08-19T04:04:43.818876713Z`
- Status/health/restarts/OOM: running / healthy / 0 / false
- Readiness/liveliness: HTTP 200 / HTTP 200
- Mounts/networks: 5 / `llm-net`, `npm_npm-net`
- Non-image environment content matched the protected rollback copy
- Compose/config/wrapper/OnePassword-wrapper hashes matched preflight
- Unrelated-container projection and 47-container count matched preflight
- PostgreSQL, Redis, admin MCP, and compatibility MCP identities and health matched preflight

Result: **PASS**
