---
id: TASK-2026-08-19-044-promote-and-finalize-stream-safe-198
complexity: standard
track: implementation
slice: polish
status: done
scr: SCR-2026-08-18-002-stream-safe-198-both-hosts
parent: TASK-2026-08-19-030-verify-cross-host-stream-safe-198
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-19-044 - Promote And Finalize Stream-Safe 1.98.0

## Objective
Create/restore the stable private tag directly at the QA-approved replacement digest, verify both hosts remain unchanged and healthy, then finalize/commit/push all intended non-secret release artifacts.

## Safety
- Promote only manifest `sha256:35fc520902eb72f5ea91ececccf221883dd5fd78b1d47c78150dfd66eb04f2d3`; no intermediate mutable reference.
- Do not recreate/restart either host, alter routing/models/auth/database/dependencies, or restore account3.
- Verify stable resolution from registry and both hosts after promotion.
- Before final commit, inspect full status/diff/log, secret-scan artifacts, close this task/current registry, and stage only intended files.
- Do not modify tracked StaticEng files after final commit.

## Acceptance Criteria
- [ ] AC-1: Stable tag is created/restored directly at the approved replacement manifest and resolves identically from registry/NAS/Fedora.
- [ ] AC-2: Both hosts remain on the exact replacement manifest/config/version/revision with unchanged container IDs/start times, healthy, zero restarts/OOM.
- [ ] AC-3: Readiness/liveliness and one final bounded public/health verification per host pass with no stream/telemetry/cache release blocker.
- [ ] AC-4: Full repository diff contains only intended source-committed history and current non-secret StaticEng SCR/task/evidence closure artifacts; no secrets detected.
- [ ] AC-5: Close task/registries before final commit; commit with required convention, push main without force, and verify clean synchronized worktree.

## Handoff
[Agent Message] From: product_manager To: tech_lead

PMA authorizes stable promotion to the exact QA-approved digest and final repository closure. Do not recreate hosts. Promote, verify, close this task/registries before commit, commit/push intended non-secret artifacts, and make no tracked changes afterward.

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations
- AC-1 passed: `docker.staticduo.com/litellm:stable` resolves directly to manifest `sha256:35fc520902eb72f5ea91ececccf221883dd5fd78b1d47c78150dfd66eb04f2d3` and config `sha256:9975f878bd5080e95ba6df47f36422b291bcf2123f32b00a81e69ca5bf7c9a3a` from the registry, NAS, and Fedora
- AC-2 passed: NAS and Fedora retained their exact container IDs, start times, pinned manifest, version 1.98.0, revision `177c66ef727710a455f058b99f653df9b3e4c0a4`, healthy status, zero restarts, and `OOM=false`
- AC-3 passed: readiness, liveliness, and one bounded public `gpt-5.6-sol` Responses check returned HTTP 200 on each host with one `response.completed` event and no stream, telemetry, cache, auth, migration, or traceback blocker
- AC-4 passed: the complete uncommitted repository set was reviewed and secret-scanned before staging; only intended source-committed history and non-secret StaticEng release closure artifacts remain
- AC-5 passed through pre-commit closure: this task is in `done`, Active is clear, the done registry row is present, and final commit/push verification is owned by the authorized Tech Lead path
- Product documentation is not required because this task changes only the release tag and closure state; steady-state behavior remains defined by the approved SCR and release architecture task
