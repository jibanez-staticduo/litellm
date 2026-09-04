---
id: TASK-2026-09-03-017-fix-internal-user-login
complexity: standard
track: implementation
slice: logic
status: todo
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-03-006-diagnose-fedora-candidate-live
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: Fix internal-user login

## Objective

Apply the smallest approved source or harness correction enabling the temporary least-privilege principal to log in exactly once through supported behavior.

## Acceptance Criteria

- [ ] AC-1: Correct only the proven login boundary without weakening authentication.
- [ ] AC-2: Add mutation-sensitive create/update/login/incorrect-password/identity/cleanup regressions.
- [ ] AC-3: Full auth/proxy/source/build/security qualification passes.
- [ ] AC-4: Tech Lead reviews, commits, pushes, rebuilds/signs if source changes; no production mutation before approval.

## Handoff

[Agent Message] From: product_manager To: developer

Do not begin until TASK-016 completes. No Fedora/NAS mutation.
