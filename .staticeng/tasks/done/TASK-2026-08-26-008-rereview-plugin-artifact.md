---
id: TASK-2026-08-26-008-rereview-plugin-artifact
complexity: standard
track: investigation
slice: qa
status: done

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations
- Approved exact 17-file release scope for `0.1.9`.
- Approved reproducible tarball SHA-256 `2c6ae123b8e00fd318410703fcaa7abe0889a65ec51043c848dacc8dddb4f49c`.
scr: SCR-2026-08-26-001-qwen38-native-reasoning-modes
parent: TASK-2026-08-26-005-plugin-only-deepseek-qwen38-config
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-26-008 - Rereview Plugin Artifact

## Objective
Independently rereview the current `0.1.9` artifact after expected Qwen3.8/documentation changes altered its checksum, establish a new approved immutable checksum, and authorize release continuation.

## Acceptance Criteria
- [ ] AC-1: Diff current source/dist/package against the previously reviewed candidate and explain every checksum-changing file semantically.
- [ ] AC-2: Confirm exact DeepSeek and Qwen3.8 variant sets and wire mappings under official OpenCode 1.18.23.
- [ ] AC-3: Run build, all tests, strict-loopback captures, package-content/local-path scans, and reproducibility check with two consecutive packs.
- [ ] AC-4: Confirm the exact intended release file scope excludes `.npmjs`, local paths, evidence, unrelated artifacts, and OpenCode core.
- [ ] AC-5: Approve one exact new SHA-256 for commit/publish or reject with findings.

## Expected Evidence
- Signed Tech Lead rereview with exact approved checksum and release scope.
