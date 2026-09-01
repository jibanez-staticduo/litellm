---
id: TASK-2026-09-01-010-integrate-upstream-main
complexity: complex
track: implementation
slice: core
status: todo
scr: SCR-2026-09-01-001-upstream-main-integration
parent: null
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: Integrate upstream main

## Objective

Integrate the exact reviewed upstream `main` into the fork, resolve all conflicts intentionally, preserve fork behavior, update dependencies/locks, and pass comprehensive source verification.

## Acceptance Criteria

- [ ] AC-1: Integration contains exact reviewed upstream commit and all prior fork commits without unresolved conflicts.
- [ ] AC-2: Conflict resolutions preserve required fork behavior and adopt upstream security/dependency fixes, including RestrictedPython >=8.5.
- [ ] AC-3: LazyMCP/OAuth, MCP, Responses, model routing, proxy, migrations, UI, and fork-specific behavior pass mapped regressions.
- [ ] AC-4: Required formatting, lint, type, lock, compile, and broader repository test gates pass with no required skips/failures.
- [ ] AC-5: Documentation and CodeMaps are updated, and complete Evidence Packet is produced.
- [ ] AC-6: Tech Lead reviews and commits the integration; no push/deployment occurs yet.

## Handoff

[Agent Message] From: product_manager To: developer

Do not begin until PMA activates this task after pre-merge closure. Use the exact architecture handoff and reviewed upstream commit. Preserve intentional fork behavior, resolve conflicts explicitly, and stop on unexplained drift. Do not push, publish, build release images, or mutate Fedora/NAS.
