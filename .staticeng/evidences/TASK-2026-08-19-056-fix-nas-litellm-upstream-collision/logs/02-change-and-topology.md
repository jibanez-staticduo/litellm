# Change and Final Topology

- Production Compose now assigns alias `litellm-production` under `npm_npm-net`
- Staging Compose no longer declares or joins `npm_npm-net`
- Staging image selector now matches production stable manifest `sha256:f44690e5203983e00a0d01016d65440bf1c4b83a941a490d22d4e7eea443b42a`
- Both Compose configurations passed `docker compose config --quiet`
- Only `litellm` and `litellm-staging` were recreated, each through `docker compose up -d --no-deps --pull never --force-recreate`
- Production Redis, both admin MCP services, staging PostgreSQL, and staging Redis retained their container identities and pre-change start times
- NPM host 62 was updated through the NPM API to `http://litellm-production:4000`
- NPM resolves `litellm-production` only to production `172.28.0.29`
- Staging has only `litellm-staging` and `llm-net`; it has no address or alias on `npm_npm-net`
- NPM reports online authenticated admin access; `nginx -t` passes
- Final production Compose SHA-256: `4514a86c3ecba2e0be2cc8f280c8592f6521ae540a9cee7a7bb2df6dd4e1356f`
- Final staging Compose SHA-256: `5d6a6b030ed2272cf96ec5ff562eee1c52c9f28afd69e79c8a925264f0a14600`
- Final NPM host 62 generated config SHA-256: `614887a180eec00c09d78cd2b22df668cd093246748ac726638f15a80e209053`
