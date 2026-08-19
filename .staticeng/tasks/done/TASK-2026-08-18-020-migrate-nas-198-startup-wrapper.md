---
id: TASK-2026-08-18-020-migrate-nas-198-startup-wrapper
complexity: standard
track: implementation
slice: foundation
status: done
scr: SCR-2026-08-18-002-stream-safe-198-both-hosts
parent: TASK-2026-08-18-010-design-stream-safe-198-release
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-18-020 - Migrate NAS 1.98.0 Startup Wrapper

## Objective
Back up and minimally migrate the NAS LiteLLM startup wrapper/Compose away from obsolete runtime source patches, then prove compatibility with the approved candidate without recreating production.

## Safety
- Fedora must remain healthy on the candidate; stable remains untouched.
- NAS production remains on healthy 1.92.0 throughout this task; do not recreate/restart services.
- Back up wrapper and Compose as a mode-0600 rollback pair with hashes before edits.
- Remove obsolete patch invocations and patch mount only after no references remain; retain host patch files as rollback artifacts.
- Preserve all database readiness/schema compatibility, retry, startup command, mounts, networks, healthcheck, and service behavior identified by architecture.

## Acceptance Criteria
- [ ] AC-1: Capture and protect exact NAS wrapper/Compose rollback pair plus current 1.92 image rollback reference.
- [ ] AC-2: Remove both runtime patch invocations and inline 1.92-only source mutation while preserving required startup behavior.
- [ ] AC-3: Remove `/app/patches` bind mount only if rendered wrapper/Compose has no runtime patch dependency; retain host files.
- [ ] AC-4: `sh -n`, rendered Compose, no-source-mutation scan, target image binary/entrypoint, and isolated wrapper compatibility checks pass against candidate digest.
- [ ] AC-5: Running NAS 1.92 service, inventory/routing, dependencies, credentials metadata, health, and Fedora remain unchanged.
- [ ] AC-6: Evidence packet records exact rollback/restoration procedure and approves or rejects NAS production deployment.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-18-020-migrate-nas-198-startup-wrapper/` with `SUMMARY.md` and sanitized logs under `logs/`.

## Handoff
[Agent Message] From: product_manager To: developer

Back up and migrate only the NAS wrapper/Compose, then validate compatibility offline/isolated against the candidate. Do not recreate production or move stable. Preserve all required startup semantics and return approve/reject for NAS deployment. Do not commit.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations
- AC-1 through AC-4 and AC-6 passed; AC-5 blocked by credential metadata/auth-flow drift.
- Wrapper/Compose migration and isolated candidate compatibility passed without production restart.
- Rollback pair is protected at `/volume2/docker/litellm/releases/20260819-wrapper-migration-b0dfe2e7a7/`.

## Blocker Report
- A credential write correlated with failed OAuth refresh and a device-auth prompt; Tech Lead rejected NAS deployment pending credential repair and permission hardening.
- Production NAS remains healthy on 1.92.0; Fedora remains healthy on the candidate; stable is unchanged.

## PMA Blocker Resolution
- Auth permissions were hardened, default/account2 refreshed, and invalid account3 quarantined with exact rollback backup.
- New exact NAS release baseline is 32 models with default primaries and account2 fallbacks; no account3 active references.
- Wrapper migration compatibility is accepted for NAS deployment with the Tech Lead just-in-time metadata/log gate.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

- AC-1 through AC-4 and AC-6 passed with sanitized evidence under `.staticeng/evidences/TASK-2026-08-18-020-migrate-nas-198-startup-wrapper/`
- The mode-0600 rollback pair is `/volume2/docker/litellm/releases/20260819-wrapper-migration-b0dfe2e7a7/`
- The live NAS wrapper/Compose no longer invokes or mounts runtime source patches; host patch files remain unchanged
- All offline and network-isolated compatibility checks passed against candidate digest `sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b`
- NAS production remained healthy on 1.92.0 without recreation or restart; Fedora and stable remained unchanged
- AC-5 failed its strict metadata equality gate because one live OAuth token mtime advanced during the task while production continued running
- NAS deployment decision: REJECT pending PMA/Tech Lead disposition and a fresh just-in-time credential metadata baseline
- No product documentation or CodeMap update is required
