---
id: TASK-2026-08-26-021A-review-release-021
complexity: standard
track: implementation
slice: polish
status: active
scr: SCR-2026-08-26-002-client-model-contracts-020
parent: TASK-2026-08-26-021-fix-020-production-discovery-shape
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-26-021A - Review and Release 0.2.1

## Objective
Independently review the 0.2.1 regression-only candidate, commit/push/publish it if approved, and prove unversioned official OpenCode resolves only 0.2.1 with no stale duplicate plugin instance.

## Acceptance Criteria
- [ ] AC-1: Review exact diff/root cause/evidence and independently reproduce live-shape behavior plus stale-duplicate diagnosis.
- [ ] AC-2: Clean build, 63 tests, dist/pack/content scans, two reproducible packs, exact approved checksum.
- [ ] AC-3: Stage/commit/push only intended five-file patch scope; exclude unrelated artifacts.
- [ ] AC-4: Publish 0.2.1 through trusted release flow or previously authorized `.npmjs` fallback if OIDC remains broken; verify npm latest/integrity/tarball.
- [ ] AC-5: In isolated official OpenCode, unversioned reference installs 0.2.1 and one plugin instance; live NAS metadata initialization succeeds.
- [ ] AC-6: Produce complete evidence and cache-invalidation guidance for Task 017.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-26-021A-review-release-021/` with `SUMMARY.md` and redacted logs.

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations

- Approved the exact five-file regression-only patch after independent live-shape, stale-cache, clean build, 63-test, tracked-dist, audit, and two-pack checksum verification.
- Committed and pushed `1d5e8e632fcfa1db03ce88a79b3ae924cadf6855`; GitHub CI passed and release `v0.2.1` was published.
- Trusted npm workflow run `33039382103` repeated the known OIDC HTTP 404 only after all identity/build/test/dist/pack/provenance gates; the authorized protected fallback published the exact checksum-pinned artifact.
- npm `latest` is 0.2.1 and the registry tarball is byte-identical to SHA-256 `ce9a42bfab697f1124376d6665619e8b11b4aa009ee9dc03de9fe702fc7b8fd6`.
- Isolated official OpenCode 1.18.23 resolved the unversioned reference to exactly one 0.2.1 instance and initialized 36 live NAS metadata models with no inference or filter error.
- No shared configuration or cache was mutated. Evidence records exact stale-cache inventory and scoped removal guidance for Task 017.
- Product and architecture documentation are not required because runtime source and generated `dist/` did not change; the test CodeMap was updated.
