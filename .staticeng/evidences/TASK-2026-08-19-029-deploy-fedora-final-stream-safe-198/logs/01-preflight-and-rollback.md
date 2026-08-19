# Fedora Fresh Preflight And Rollback Readiness

- Captured: `2026-08-19T02:26:36Z`
- Running image before deployment: `docker.staticduo.com/litellm@sha256:2e947963eddbd9385e618d5bd3e122f41a5677a05b843b5add29cef3d52991e9`
- Status/health/restarts/OOM: running / healthy / 0 / false
- Readiness/liveliness: HTTP 200 / HTTP 200
- Rollback local image: available
- Rollback registry digest: resolvable
- Candidate registry digest: resolvable
- Stable manifest: `sha256:b52c0949442e8855289df706621725670d1cff28738a277c245b273b388873e0`
- Public/deployment rows: 27 / 27
- Default-qualified/account2-qualified rows: 7 / 7
- Public GPT aliases: 6
- Fallback rules: 24, bidirectional cross-profile policy enabled
- Public projection SHA-256: `6e544c6f67be0079b5bfbe7bf7a0d34fad1a5746bfafb92f17cbf8cb36b28981`
- Deployment projection SHA-256: `379457f5c8ece93db75eb5cf578668459f56a1dc02025dd05bb6c3f4d5601863`
- Router projection SHA-256: `ab1685115bff384b55c5a1d095143b7970bdee3c80587320801039aca46b0114`
- Compose/config/wrapper/OnePassword wrapper SHA-256: `af1a6462...d6`, `f3b83ce7...67`, `9e9b0de7...6e`, `31f719b7...89`
- Credential metadata: five regular non-symlink files, exact expected owners/modes/sizes/mtimes/inodes/devices; credential contents not read
- Dependencies: Redis and both admin MCP containers healthy with exact IDs
- Running containers: 47
- LiteLLM mounts/networks: 5 / `llm-net`, `npm_npm-net`

Result: **PREFLIGHT AND ROLLBACK READINESS PASS**
