---
id: TASK-2026-08-26-016-publish-opencode-litellm-020
complexity: standard
track: implementation
slice: polish
status: active
scr: SCR-2026-08-26-002-client-model-contracts-020
parent: TASK-2026-08-26-015-implement-020-model-contracts
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 1
---

# Task: TASK-2026-08-26-016 - Publish opencode-litellm 0.2.0

## Objective
Commit the exact approved Task-015 scope, publish GitHub release `v0.2.0` through trusted OIDC npm publishing, and verify isolated unversioned resolution before any shared client migration.

## Acceptance Criteria
- [ ] T2-AC-1: Reconfirm exact scope/checksum/status/log/remotes; stage and commit only reviewed files; push non-force with CI green and tracked dist clean.
- [ ] T2-AC-2: Create exact annotated tag/release identity `v0.2.0` for `@staticeng/opencode-litellm@0.2.0` without altering reviewed source.
- [ ] T2-AC-3: GitHub release triggers the existing trusted-publishing workflow using OIDC/provenance; no npm token or `.npmjs` is used.
- [ ] T2-AC-4: npm reports `0.2.0` as published/latest with expected provenance, integrity, and exact tarball contents.
- [ ] T2-AC-5: Isolated official OpenCode resolves unversioned `@staticeng/opencode-litellm` to installed `0.2.0` and passes representative GPT/DeepSeek/Qwen/override/retirement probes.
- [ ] T2-AC-6: Produce complete evidence with commit/tag/release/workflow/npm URLs and rollback/dist-tag guidance.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-26-016-publish-opencode-litellm-020/` with `SUMMARY.md` and redacted logs.

## Stop Conditions
Stop before further mutation on scope/checksum drift, non-fast-forward/conflict, failing CI/workflow, provenance/integrity mismatch, npm resolution mismatch, or behavioral probe failure.

## Reopen History

### Reopen 1 - 2026-08-26
- GitHub CI/tag/release passed, but npm trusted publishing failed with HTTP 404 after OIDC/provenance generation.
- User authorized a one-time `.npmjs` token fallback for the exact immutable `v0.2.0` artifact.
- Resume only publication, registry verification, and isolated unversioned resolution; do not move/recreate the tag or alter source.

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations

- Exact reviewed scope was committed as `21f6583e9b4a112c0d2be79bbd102333de72bd89`, pushed non-force, and passed CI.
- Reproducible package SHA-256 remained `40b2ce710ec8cba570742d8f86c541ef06dba0e8d119db0d66bb91185487fcba`; tracked `dist/` was clean and package inventory remained 19 files.
- Signed annotated tag and GitHub release `v0.2.0` were created against the exact commit.
- Trusted OIDC publish workflow run `32964753523` failed only at the final npm registry PUT with HTTP 404 after identity, ancestry, build, 62 tests, tracked-dist, pack, and provenance-signing gates passed.
- Stop condition was enforced. npm still reports `latest=0.1.9` and no `0.2.0`; no retry, token fallback, dist-tag mutation, unversioned OpenCode probe, or client migration occurred.
- Task is blocked pending PMA-coordinated owner verification/correction of npm trusted-publisher authorization. Full redacted evidence is under `.staticeng/evidences/TASK-2026-08-26-016-publish-opencode-litellm-020/`.
- Product documentation is not additionally required; existing package documentation remains accurate, and this task adds operational release evidence only.
- `staticeng_validate` remains blocked by the governing workspace's pre-existing unrelated CodeMap backlog. Required repair dry-run was performed; safe apply was withheld because it proposed unrelated mutations and unresolved manual module boundaries.

### Reopen 1 - Tech Lead Fallback Attempt

- User-authorized one-time `.npmjs` fallback was preflighted without reading, printing, copying, or modifying the protected credential. The file remained ignored and mode `0600`.
- A fresh detached worktree of the existing immutable `v0.2.0` tag resolved to commit `21f6583e9b4a112c0d2be79bbd102333de72bd89` and was clean before verification.
- Clean `npm ci`, build, 62/62 tests, and tracked-dist comparison passed. The clean-tag pack contained the expected 19 files, but its SHA-256 was `2ac50fc9ab952c2ac244b73bcbe23eadf4b0fd530085e4a0c8d823749d7c82c6`, not the authorized reviewed SHA-256 `40b2ce710ec8cba570742d8f86c541ef06dba0e8d119db0d66bb91185487fcba`.
- The mismatch occurred before `npm publish`; the stop condition was enforced immediately. No credential-backed command, npm mutation, source/tag/release change, shared configuration change, or OpenCode probe occurred. npm `latest` remains `0.1.9` and `0.2.0` remains absent.
- Reopen 1 remains blocked pending PMA direction. The reviewed checksum cannot currently be reproduced from a standard clean checkout of the immutable tag, and publication is not authorized without resolving that discrepancy.
