---
id: TASK-2026-08-21-fix-coordination-redis-wiring
title: Restore coordination Redis wiring and release LiteLLM
complexity: standard
track: implementation
slice: foundation
status: done
assigned_to: tech_lead
handoff_from: product_manager
scr: none
parent: TASK-2026-08-21-coordination-redis-warning
created: 2026-08-21
---

# Task

Restore the missing coordination Redis imports and router registration in the authoritative LiteLLM fork, add focused regression coverage, commit and push the fix to `main`, build/publish an immutable replacement image, deploy it to the LiteLLM stack, and verify the defect is resolved without regressions.

# Acceptance Criteria

- AC-1: Reconfirm missing source wiring and restore the persisted-settings function import, router import, and one router registration.
- AC-2: Cover startup symbol wiring, persisted initialization, single registration, and authenticated route availability with passing focused tests and quality checks.
- AC-3: Preserve unrelated source/worktree changes and commit only intended files.
- AC-4: Commit on `main` and push to verified `origin/main` without force.
- AC-5: Build and push an immutable image from the pushed product-fix commit using safe release overrides and no upstream merge.
- AC-6: Deploy with rollback information and leave LiteLLM and Redis healthy.
- AC-7: Verify readiness, Redis cache, representative routing, authorized/unauthorized coordination access, persisted initialization, and absence of the startup NameError warning.
- AC-8: Produce complete redacted evidence with AC mapping and provenance.

# Handoff

[Agent Message] From: product_manager To: tech_lead

BA review accepted. Implement the confirmed bounded repair, separate implementation and technical verification phases, then commit/push `main`, publish and deploy the immutable image with safe release overrides, and produce complete redacted evidence.

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations

- AC-1 through AC-8 pass; detailed mapping is in `.staticeng/evidences/TASK-2026-08-21-fix-coordination-redis-wiring/SUMMARY.md`.
- Product fix `eceb5129d3d29bd73bd446be2aa75d955f782d69` is pushed to `origin/main`.
- Immutable release digest is `sha256:002358c594940dc7a78796062b3af2a11a48eb370531207d5059f8f61e71865d`.
- Rollback tag is `docker.staticduo.com/litellm:rollback-task-20260821-coordination-redis-20260821-104623`.
- No steady-state product, architecture, or technical documentation update is required because this restores already-intended wiring.
