---
id: TASK-2026-08-19-058-harden-nas-litellm-npm-permissions
complexity: standard
track: implementation
slice: foundation
status: done
scr: null
parent: TASK-2026-08-19-057-verify-nas-upstream-collision-fix
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-19-058 - Harden NAS LiteLLM And NPM Permissions

## Objective
Harden pre-existing world-writable LiteLLM secret-bearing configuration and NPM host-62 runtime configuration while preserving NPM regeneration and live services.

## Safety
- Never read, print, hash, copy into evidence, or expose secret values.
- Capture only path/type/symlink/owner/mode/size/mtime/inode metadata and protected rollback copies.
- Do not restart/recreate LiteLLM or NPM unless permission changes demonstrably require a supported reload.
- Preserve public routing, TLS, DB, models, credentials, containers, networks, and unrelated NPM hosts.

## Acceptance Criteria
- [ ] AC-1: Inventory affected LiteLLM `.env`/parent and NPM host-62 file/parents metadata without reading contents; create protected mode-0600 rollback where safe.
- [ ] AC-2: LiteLLM secret-bearing `.env` becomes owner-only 0600 and necessary deployment directories lose world-write while retaining service access.
- [ ] AC-3: NPM host-62 config and minimum required parent permissions become non-world-writable using ownership/modes compatible with NPM regeneration.
- [ ] AC-4: Trigger or observe one supported NPM regeneration/reload cycle and prove hardened permissions persist or define a durable post-generation enforcement mechanism.
- [ ] AC-5: Public TLS/routing, repeated Codex, chat, LazyMCP, production/staging health, dependencies, restarts/OOM, and unrelated NPM hosts remain functional.
- [ ] AC-6: Evidence is sanitized and maps all ACs; no secrets exposed.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-19-058-harden-nas-litellm-npm-permissions/` with sanitized metadata logs.

## Handoff
[Agent Message] From: product_manager To: developer

Harden the pre-existing world-writable LiteLLM `.env`/deployment path and NPM host-62 runtime permissions without exposing contents or disrupting regeneration. Preserve all services and verify full public functionality. Do not commit.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations
- AC-1 through AC-6 passed.
- Production/staging `.env` files are 0600; required deployment paths are non-world-writable.
- NPM host 62 is root-owned 0644 with root-owned 0755 parents and survives supported regeneration.
- TLS, routing, three Codex SSE probes, chat, LazyMCP, inventories, dependencies, restarts/OOM, DNS, logs, and unrelated NPM hosts passed.

## PMA Final Closure
- Permission hardening accepted based on complete functional and regeneration verification.
- No product or architecture documentation update required.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

- AC-1 through AC-6 passed without restart, recreation, or rollback
- Hardened production and staging secret-bearing `.env` files to owner-only `0600`
- Removed world-write from required LiteLLM deployment paths, launchers, releases, and shared `/volume2/docker` parent while preserving deployment-owner access
- Hardened NPM host 62 to root-owned `0644` and required NPM parents to root-owned `0755`
- Proved supported NPM API regeneration recreates host 62 directly as `0644`; Nginx syntax, container parent-write access, and delayed durability passed
- Passed TLS, public/staging health, three repeated Codex SSE probes, chat, LazyMCP/admin inventory, DNS/routing, dependencies, restarts/OOM, unrelated-host permission inventory, and clean bounded logs
- Created sanitized evidence under `.staticeng/evidences/TASK-2026-08-19-058-harden-nas-litellm-npm-permissions/`; no secret values or hashes were retained
- No product/architecture/source/CodeMap documentation update is required; this evidence records the durable NAS permission contract
- Preserved unrelated worktree artifacts and created no commit
