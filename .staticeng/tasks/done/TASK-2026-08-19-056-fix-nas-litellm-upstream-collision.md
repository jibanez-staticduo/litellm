---
id: TASK-2026-08-19-056-fix-nas-litellm-upstream-collision
complexity: standard
track: implementation
slice: foundation
status: done
scr: null
parent: TASK-2026-08-19-055-diagnose-local-codex-failure
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-19-056 - Fix NAS LiteLLM Upstream Collision

## Objective
Remove stale staging from public LiteLLM traffic by assigning production a unique shared-network alias and pointing NPM proxy host 62 exclusively to it, then upgrade staging to the current stable image so the stream failure cannot recur through either environment.

## Safety
- Back up production/staging Compose and NPM host 62 config with mode 0600 and hashes before mutation.
- Preserve production container/image, DB, models/routing, credentials, dependencies, networks, and public TLS/domain behavior.
- Do not automatically roll back; per user instruction, diagnose and repair in place if a check fails.
- Recreate only the minimum affected services with `--no-deps`; do not restore DB or alter account topology.
- Preserve unrelated primary-worktree Fedora artifacts.

## Acceptance Criteria
- [x] AC-1: Capture exact pre-change DNS resolution, container/network aliases, NPM upstream config, images/revisions, health, and rollback files.
- [x] AC-2: Production has a unique `npm_npm-net` alias such as `litellm-production`; NPM host 62 targets only that alias and resolves to exactly production.
- [x] AC-3: Staging no longer registers the ambiguous `litellm` alias on the public proxy network and is upgraded to current stable manifest/revision or removed from public network resolution.
- [x] AC-4: Public domain repeatedly resolves/routes only to production; staging access logs receive zero public requests during bounded verification.
- [x] AC-5: Repeated native Codex `/v1/responses` checks pass HTTP 200 SSE without `Stream must be set to true`; public chat/health and LazyMCP compatibility remain functional.
- [x] AC-6: Production/staging health, restart/OOM, topology/preservation, NPM health, TLS/public access, and clean logs pass.
- [x] AC-7: Evidence packet maps all ACs and records durable topology/runbook impact.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-19-056-fix-nas-litellm-upstream-collision/` with `SUMMARY.md` and sanitized logs.

## Handoff
[Agent Message] From: product_manager To: developer

Fix the NAS production/staging Docker DNS collision in place. Back up first, give production a unique proxy alias, repoint NPM host 62, remove staging ambiguity, and upgrade staging to current stable. Do not automatically roll back. Verify repeated public Codex requests hit production only and preserve all production state. Do not commit.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

- AC-1 through AC-7 passed without rollback
- Backed up both Compose files and NPM host 62 generated config with owner-only permissions and verified hashes
- Assigned production alias `litellm-production`, removed staging from `npm_npm-net`, and repointed NPM host 62 exclusively to production
- Upgraded staging to stable manifest `sha256:f44690e5203983e00a0d01016d65440bf1c4b83a941a490d22d4e7eea443b42a`, revision `8589869e1c`
- Recreated only production and staging LiteLLM services with `--no-deps`; all dependencies retained their prior identities and start times
- Passed five repeated public native Responses SSE probes with HTTP 200, completion events, no SSE errors, and no `Stream must be set to true`
- Passed public/staging health, public chat, model inventory, LazyMCP inventory, NPM/TLS, DNS isolation, restart/OOM, and bounded clean-log checks
- Created complete sanitized evidence under `.staticeng/evidences/TASK-2026-08-19-056-fix-nas-litellm-upstream-collision/`
- Updated operational documentation impact in the evidence packet; repository CodeMaps are incomplete, but no source navigation changed
- Preserved unrelated worktree artifacts and created no commit
