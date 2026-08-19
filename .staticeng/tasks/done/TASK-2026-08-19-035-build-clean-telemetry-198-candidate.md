---
id: TASK-2026-08-19-035-build-clean-telemetry-198-candidate
complexity: standard
track: implementation
slice: foundation
status: done
scr: SCR-2026-08-18-002-stream-safe-198-both-hosts
parent: TASK-2026-08-19-032-fix-release-telemetry-tracebacks
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-19-035 - Build Clean-Telemetry 1.98.0 Candidate

## Objective
Build and push one immutable replacement LiteLLM 1.98.0 image from clean commit `177c66ef727710a455f058b99f653df9b3e4c0a4`, containing stream guards plus telemetry/cache fixes, without deployment or tag promotion.

## Acceptance Criteria
- [ ] AC-1: Build exactly once from clean synchronized main, linux/amd64, version 1.98.0, expected OCI revision/version.
- [ ] AC-2: Push only one unique candidate tag and resolve manifest/config digests; stable remains unchanged/missing.
- [ ] AC-3: Image inspection proves stream guards, logging-state synchronization, fake-stream bypass, and restored `_init_cache` contract.
- [ ] AC-4: Focused stream/telemetry/cache regression suites and bounded image import/introspection pass without failures/skips.
- [ ] AC-5: Capture current both-host rollback/identity baselines and produce sequential Fedora-then-NAS deployment gate.
- [ ] AC-6: Complete sanitized evidence approves/rejects candidate deployment.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-19-035-build-clean-telemetry-198-candidate/` with `SUMMARY.md` and logs.

## Handoff
[Agent Message] From: product_manager To: developer

Build/push exactly one replacement candidate from commit `177c66ef727710a455f058b99f653df9b3e4c0a4`. Do not deploy or move stable/latest. Prove all source fixes, tests, identities, and current rollback baselines. Do not commit.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations
- AC-1 through AC-6 passed.
- Candidate manifest `sha256:35fc520902eb72f5ea91ececccf221883dd5fd78b1d47c78150dfd66eb04f2d3`, config `sha256:9975f878bd5080e95ba6df47f36422b291bcf2123f32b00a81e69ca5bf7c9a3a`.
- Built once from commit `177c66ef727710a455f058b99f653df9b3e4c0a4`; 350 tests passed.
- Stable and both hosts remained unchanged.

## QA Engineer: Post Implementation Expectations
- Independently approved Fedora-first immutable deployment.
- Identity, all in-image contracts, 14 focused tests, stable non-promotion, and rollback baselines passed.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

- AC-1 through AC-6 passed with sanitized evidence under `.staticeng/evidences/TASK-2026-08-19-035-build-clean-telemetry-198-candidate/`
- Exactly one `linux/amd64` image was built from clean synchronized commit `177c66ef727710a455f058b99f653df9b3e4c0a4` and exactly one unique candidate tag was pushed
- Immutable candidate: `docker.staticduo.com/litellm@sha256:35fc520902eb72f5ea91ececccf221883dd5fd78b1d47c78150dfd66eb04f2d3`
- Config digest/image ID: `sha256:9975f878bd5080e95ba6df47f36422b291bcf2123f32b00a81e69ca5bf7c9a3a`
- Focused stream, telemetry, terminal logging, cache, auth-cache, and poller suites passed 350 tests with no failures or skips; installed-image import/introspection passed all required fix assertions
- Current NAS and Fedora rollback/identity baselines were captured, and the sequential Fedora-then-NAS deployment gate was recorded
- Both hosts remained unchanged and healthy; stable remained `sha256:b52c0949442e8855289df706621725670d1cff28738a277c245b273b388873e0`
- No deployment, stable/latest movement, source change, host file mutation, or commit was performed
- Product, architecture, and CodeMap documentation are unchanged because this task created only a release artifact and operational evidence
- `staticeng_validate` remains blocked by inherited broken links and repository-wide missing CodeMaps; broad unrelated dry-run repairs were not applied
