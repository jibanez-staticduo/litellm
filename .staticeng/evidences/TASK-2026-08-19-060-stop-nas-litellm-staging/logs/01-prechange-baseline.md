# Pre-change Baseline

Captured immediately before action:

- Staging: container `d417de53cff9...`, image manifest `sha256:f44690e5...3b42a`, image ID `sha256:84dd79e3...ceed`, running, healthy, restart `unless-stopped`, zero restarts, OOM false
- Staging Compose: project `litellm-staging`, service `litellm`, workdir `/volume2/docker/litellm-staging`, config `/volume2/docker/litellm-staging/docker-compose.yaml`
- Staging topology: six bind mounts, private staging network plus internal `llm-net`, loopback port `127.0.0.1:14000`, readiness/liveliness HTTP 200
- Staging dependencies: PostgreSQL `25a7ab4c0c4...` and Redis `e69e7ef095b0...`, both running and healthy with zero restarts/OOM
- Production: container `3d92b5aa1f96...`, independently running and healthy, restart `unless-stopped`, zero restarts, OOM false
- Production proxy DNS: NPM resolved `litellm-production` to only `172.28.0.29`
- NPM: container `a61ce465010f...`, running and healthy with zero restarts/OOM; Nginx syntax passed
- Public readiness/liveliness: HTTP 200; TLS verification result 0
- Staging Compose SHA-256: `5d6a6b030ed2272cf96ec5ff562eee1c52c9f28afd69e79c8a925264f0a14600`
- NPM host 62 SHA-256: `614887a180eec00c09d78cd2b22df668cd093246748ac726638f15a80e209053`

No environment values, authorization values, prompts, responses, or config contents were retained
