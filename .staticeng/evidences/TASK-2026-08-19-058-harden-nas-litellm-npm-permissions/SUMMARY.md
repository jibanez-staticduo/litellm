# NAS LiteLLM And NPM Permission Hardening

## Summary

Hardened both NAS LiteLLM secret-bearing `.env` files and their deployment paths, plus NPM host 62 and its required parent path, without restarting or recreating any service

## Work Performed

- Inventoried only path/type/symlink/owner/mode/size/mtime/inode and ACL metadata; secret values and hashes were never retained
- Created root-owned rollback copies under `/volume2/docker/litellm/releases/20260819T160419Z-TASK-2026-08-19-058-harden-nas-litellm-npm-permissions`
- Set production and staging `.env` files to owner-only `0600`; hardened deployment directories, launchers, releases, and the shared `/volume2/docker` parent
- Set NPM runtime parents to root-owned `0755` and generated host 62 to root-owned `0644`
- Triggered a supported no-op NPM host 62 API update; regeneration retained the same config size/content and recreated host 62 directly as `0644`
- Verified public TLS/routing, three Codex Responses probes, public chat, LazyMCP/admin inventory, production/staging health, dependencies, restart/OOM state, NPM syntax/DNS, unrelated NPM hosts, and clean bounded logs

## Acceptance Criteria Coverage

- **AC-1: PASS**. Metadata-only inventory covered both `.env` files, deployment parents, NPM host 62, and NPM parents. Protected rollback directory is `0700`; rollback files and metadata are root-owned `0600`
- **AC-2: PASS**. Production and staging `.env` files are owner-only `0600`. Required deployment paths are non-world-writable while the deployment owner retains required read/write/execute access
- **AC-3: PASS**. NPM host 62 is root-owned `0644`; `/volume2/docker/npm`, `data`, `nginx`, and `proxy_host` are root-owned `0755`, allowing root-running NPM regeneration without world-write
- **AC-4: PASS**. A supported NPM API update regenerated and reloaded host 62. The inode changed, content remained byte-identical, mode remained `0644`, `nginx -t` passed, and a container-side create/remove probe proved parent write access
- **AC-5: PASS**. Public TLS and both health endpoints passed. Three Codex SSE requests and one chat request passed HTTP 200. LazyMCP exposed 23 servers/488 tools, admin health reported DB connectivity, and admin inventories returned 23 MCP servers and 32 models. Production, staging, dependencies, and NPM remained healthy with unchanged start times, zero restarts, and OOM false. NPM resolved `litellm-production` only to production, all 112 generated proxy-host configs were non-world-writable, and a final bounded log window was clean
- **AC-6: PASS**. Evidence contains only sanitized metadata, counts, statuses, and pass/fail results. It contains no secret contents, hashes, authorization values, prompts, or response contents

## Documentation Impact

No product, architecture, application-source, or CodeMap change is required. Durable NAS operational truth is recorded in this evidence packet: production/staging `.env` files are `0600`; NPM runtime parents are `0755`; generated proxy-host configs are `0644` and retain that mode through supported regeneration

## Open Risks

- The parent `/volume2/docker` was hardened from `0777` to `0770`; members of the NAS `admin` group retain full deployment access, while non-group users no longer have traversal
- NPM generated configs remain world-readable at `0644`, matching conventional Nginx config behavior and avoiding regeneration issues; they are no longer world-writable
- Two malformed verification attempts generated expected HTTP 400 errors before the corrected `gpt-5.6-sol` Codex probes passed; the final bounded log window was clean
- Staging Compose references required `STAGING_DB_PASSWORD` interpolation not present in its local `.env`; this pre-existing issue prevented a full staging `docker compose config` parse but did not affect file access or the healthy running deployment

## Recommended Next Step

PMA should route the packet to independent QA and retain the protected rollback directory until closure
