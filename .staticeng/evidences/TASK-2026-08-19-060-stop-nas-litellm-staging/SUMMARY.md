# NAS LiteLLM Staging Stop

## Summary

Stopped only the NAS `litellm-staging` application container and changed its runtime restart policy to `no`, preserving the stopped container, image, mounts, networks, configuration, data, PostgreSQL, Redis, and all production services

## Work Performed

- Captured sanitized staging and production identity, image, health, restart, Compose, network, mount, dependency, DNS, NPM, and public endpoint baselines
- Used the staging Compose project to stop only service `litellm`
- Applied `docker update --restart=no litellm-staging` so Docker cannot automatically relaunch the stopped container
- Observed the exact container identity in stopped state for more than 45 seconds
- Verified production public health, Codex Responses SSE, chat completions, LazyMCP status/describe/call, TLS, DNS, NPM syntax/upstream, and dependency preservation
- Documented a manual restart procedure that restores the normal Compose restart policy without removing or recreating staging

## Acceptance Criteria Coverage

- **AC-1: PASS**. Before action, staging container `d417de53cff9...` was running and healthy on the stable manifest with restart policy `unless-stopped`, Compose project `litellm-staging`, service `litellm`, six mounts, two private/internal networks, and healthy PostgreSQL/Redis dependencies. Production container `3d92b5aa1f96...` was independently running and healthy
- **AC-2: PASS**. The staging Compose service stop targeted only `litellm`. Its exact container remains present and exited; staging PostgreSQL and Redis retained their identities, start times, and healthy running state
- **AC-3: PASS**. After a greater-than-45-second bounded observation, the exact staging container remained exited with `restart=no`, zero restarts, and OOM false
- **AC-4: PASS**. Production retained its identity/start time and remained healthy with zero restarts/OOM. Public readiness/liveliness, Codex SSE, chat, LazyMCP, NPM/TLS, production-only proxy DNS, and all checked dependencies passed
- **AC-5: PASS**. The Compose file hash remained `5d6a6b...a14600`; the stopped container retains six mounts and two networks; the exact stable image remains locally present. Configuration/data/dependency paths were not changed. The manual restart procedure is documented below
- **AC-6: PASS**. Evidence contains only sanitized identifiers, hashes, status, counts, and endpoint classifications. No secret values, prompts, or responses were retained. No commit was created and unrelated worktree artifacts were preserved

## Manual Restart Procedure

Run on the NAS:

```sh
docker update --restart=unless-stopped litellm-staging
docker start litellm-staging
docker inspect --format 'status={{.State.Status}} health={{if .State.Health}}{{.State.Health.Status}}{{end}} restart={{.HostConfig.RestartPolicy.Name}}' litellm-staging
curl -fsS http://127.0.0.1:14000/health/readiness >/dev/null
```

This starts the preserved container directly and restores the policy declared by Compose. It does not recreate the container or start/stop dependencies

## Documentation Impact

No product, architecture, application source, or CodeMap documentation changed. This evidence packet is the operational record for the reversible staging stop and manual restart procedure

## Open Risks

- The staging Compose file still declares `restart: unless-stopped`; the existing container is protected by runtime policy `no`, but a future `docker compose up` that recreates it will restore the declared policy and start staging
- Docker records exit code 137 for the Compose stop because the application did not finish before the stop timeout; OOM is false, the state error is empty, and no container was removed
- PostgreSQL and Redis intentionally remain running and retain their own `unless-stopped` policies because the task requires preserving dependencies
- `staticeng_validate` remains blocked by inherited broken `.staticeng/codemap.yml` links and repository-wide missing CodeMaps. The repair dry-run proposes broad unrelated changes, so it was not applied

## Recommended Next Step

PMA should route this evidence packet for closure. Use the documented direct-container procedure only when staging is intentionally needed again
