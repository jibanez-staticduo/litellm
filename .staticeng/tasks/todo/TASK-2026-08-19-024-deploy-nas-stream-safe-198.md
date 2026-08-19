---
id: TASK-2026-08-19-024-deploy-nas-stream-safe-198
complexity: standard
track: implementation
slice: foundation
status: active
scr: SCR-2026-08-18-002-stream-safe-198-both-hosts
parent: TASK-2026-08-18-010-design-stream-safe-198-release
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-19-024 - Deploy NAS Stream-Safe 1.98.0

## Objective
Deploy the same verified immutable 1.98.0 candidate to NAS using the migrated wrapper, preserve the new 32-model default/account2 baseline, and execute every functional/preservation gate.

## Safety
- Candidate digest: `sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b`.
- Fedora must remain healthy on the same candidate; stable remains untouched until cross-host QA.
- Capture just-in-time credential metadata/log baseline within 60 seconds of deployment using the Tech Lead gate; never read credential contents.
- Preserve the protected 1.92 image plus wrapper/Compose rollback pair and account3 quarantine backup.
- Recreate only NAS `litellm` with `--no-deps`; no DB restore, model/routing/auth mutation, or dependency recreation.
- Roll back NAS image and wrapper/Compose pair on any failure; if release cannot be completed, restore Fedora to avoid split state.

## Acceptance Criteria
- [ ] AC-1: Just-in-time baseline passes with no recent auth/device-flow failure, safe 0700/0600 permissions, exact 32-model/routing hash, dependency identities, and rollback readiness.
- [ ] AC-2: NAS runs the pinned 1.98.0 digest/version/revision through the migrated wrapper; only LiteLLM is recreated.
- [ ] AC-3: Health/readiness/liveliness, restart/OOM, 10-minute observation, startup/schema/migration, and clean-log gates pass.
- [ ] AC-4: Exact 32-model baseline, default primaries, account2 fallbacks/qualified deployments, unrelated routes, protected hashes, credentials metadata, dependencies, volumes, and networks are preserved; account3 remains quarantined.
- [ ] AC-5: Native Responses client `stream=false`, corrected Codex default/account2/public fallback checks pass without stream/auth/device errors and with correct profile selection.
- [ ] AC-6: LazyMCP status, describe, tool-list, and one harmless configured tool smoke pass.
- [ ] AC-7: Fedora remains healthy and unchanged on the same candidate; stable remains unchanged.
- [ ] AC-8: Complete evidence packet records deployment and rollback proof and approves/rejects final cross-host promotion.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-19-024-deploy-nas-stream-safe-198/` with `SUMMARY.md` and sanitized logs under `logs/`.

## Handoff
[Agent Message] From: product_manager To: developer

Deploy only NAS by the exact candidate digest using the validated wrapper and strict just-in-time credential gate. Preserve the 32-model default/account2 baseline and quarantined account3 state. Execute every gate, roll back on failure, keep Fedora/stable unchanged, and do not commit.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

- Three fresh just-in-time gates passed before bounded deployment attempts
- Each attempted candidate recreation was stopped by a deployment-harness assertion and automatically rolled back to the protected NAS 1.92.0 image plus wrapper/Compose pair
- The third attempt identified a manifest-versus-config-ID assertion mismatch: manifest `42d365...115b`, NAS-local config ID `45a019...c73`
- Strict credential comparison also found recurring ctime-only drift on one salted lock-file path with every other metadata field unchanged and no correlated auth/device-flow logs
- NAS final rollback health, exact 32-model/routing topology, dependencies, and account3 quarantine pass
- Fedora was restored to its pre-release digest after release failure as required to avoid split state; stable was not changed
- Candidate Responses, Codex, and LazyMCP gates were not run after the mandatory stop
- Cross-host promotion is rejected pending Tech Lead review through PMA
- No product/architecture/CodeMap update is required and no commit was created
