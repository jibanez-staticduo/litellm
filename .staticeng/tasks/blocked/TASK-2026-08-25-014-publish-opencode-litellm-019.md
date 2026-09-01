---
id: TASK-2026-08-25-014-publish-opencode-litellm-019
complexity: standard
track: implementation
slice: polish
status: blocked

## Blocker Report
- npm authentication preflight returned `E401 Unauthorized`.
- No files were staged, committed, pushed, packed, published, or activated locally.
- Resume after authorized npm credentials are restored and `npm whoami` succeeds.
scr: SCR-2026-08-25-001-deepseek-v4-native-reasoning-modes
parent: TASK-2026-08-25-011-implement-opencode-litellm-deepseek-variants
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-25-014 - Publish opencode-litellm 0.1.9

## Objective
Commit, push, and publish the independently approved exact `@staticeng/opencode-litellm@0.1.9` release candidate.

## Acceptance Criteria
- [ ] AC-1: Reconfirm git status/diff/log, npm identity, and exact ten-file release scope before staging.
- [ ] AC-2: Stage and commit only the ten approved files using the repository's commit convention; exclude every unrelated change.
- [ ] AC-3: Push the release commit to the existing authorized fork/branch without force.
- [ ] AC-4: Rebuild/pack and prove artifact integrity is materially identical to the reviewed candidate, then publish `0.1.9` to npm.
- [ ] AC-5: Verify npm registry metadata/integrity and package contents after publish.
- [ ] AC-6: Produce complete evidence and rollback/repin guidance; do not edit live OpenCode config in this task.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-25-014-publish-opencode-litellm-019/` with `SUMMARY.md` and redacted logs.

## Acceptance Criteria Verification Map
- [ ] AC-1
  - **Method:** pre-release inspection
  - **Evidence:** evidence packet
- [ ] AC-2
  - **Method:** commit inspection
  - **Evidence:** evidence packet
- [ ] AC-3
  - **Method:** remote verification
  - **Evidence:** evidence packet
- [ ] AC-4
  - **Method:** package build and npm publish
  - **Evidence:** evidence packet
- [ ] AC-5
  - **Method:** npm registry verification
  - **Evidence:** evidence packet
- [ ] AC-6
  - **Method:** closure review
  - **Evidence:** SUMMARY.md

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations

- Release preflight confirmed the approved ten-file scope, `main` tracking `origin/main`, authorized fork remote, package metadata at `0.1.9`, and registry availability of versions through `0.1.8`
- npm identity verification failed with `E401 Unauthorized` before staging, commit, push, pack, or publish
- Per the task's authentication failure rule, no authentication bypass or alternate credentials were attempted and no release commit was created
- No live OpenCode configuration, unrelated release-repository files, package registry state, or LiteLLM product source was modified
- Resume from npm authentication verification, then repeat the complete preflight before staging the exact approved ten files
