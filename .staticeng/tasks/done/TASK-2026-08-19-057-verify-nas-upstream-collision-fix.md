---
id: TASK-2026-08-19-057-verify-nas-upstream-collision-fix
complexity: standard
track: investigation
slice: qa
status: done
scr: null
parent: TASK-2026-08-19-056-fix-nas-litellm-upstream-collision
assigned_to: qa_engineer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-19-057 - Verify NAS Upstream Collision Fix

## Objective
Independently verify public LiteLLM traffic reaches production only, staging is isolated and current, and the Codex stream error cannot recur through Docker DNS round-robin.

## Acceptance Criteria
- [ ] AC-1: NPM host 62 targets unique `litellm-production`; DNS resolves it to exactly production and generic `litellm` has no staging address.
- [ ] AC-2: Staging is absent from `npm_npm-net`, current on stable revision, and healthy on private/loopback access.
- [ ] AC-3: Repeated public native Responses/Codex probes return HTTP 200 SSE with no stream error and correlate only to production logs.
- [ ] AC-4: Public chat, LazyMCP, TLS/NPM health, production/staging health, topology, dependencies, restarts/OOM, and preservation pass.
- [ ] AC-5: Review backup/evidence security and approve/reject final closure.

## Handoff
[Agent Message] From: product_manager To: qa_engineer

Perform independent read-only live QA of the NAS NPM/Docker network correction. Verify production-only public routing, staging isolation/current revision, repeated Codex success, and all preservation/security gates. Do not mutate anything. Return explicit closure approval/rejection.

# Post Implementation Task Updates

## QA Engineer: Final Approval
- AC-1 through AC-5 passed through independent live verification.
- Public host 62 targets only `litellm-production:4000`; staging is absent from `npm_npm-net` and current on stable revision.
- Five corrected public native Codex requests passed HTTP 200 SSE and correlated only to production logs; staging saw zero public Responses requests.
- Chat, LazyMCP, TLS, NPM, dependencies, topology, health, restarts/OOM, backups, hashes, and evidence security passed.

## PMA Final Closure
- Parent collision fix and verification accepted.
- Separate security hardening is warranted for pre-existing world-writable `.env` and NPM runtime-tree permissions.
