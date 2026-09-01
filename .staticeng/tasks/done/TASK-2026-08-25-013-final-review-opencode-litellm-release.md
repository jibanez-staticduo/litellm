---
id: TASK-2026-08-25-013-final-review-opencode-litellm-release
complexity: standard
track: investigation
slice: qa
status: done
scr: SCR-2026-08-25-001-deepseek-v4-native-reasoning-modes
parent: TASK-2026-08-25-011-implement-opencode-litellm-deepseek-variants
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-25-013 - Final Review opencode-litellm Release

## Objective
Perform final release-readiness review of `@staticeng/opencode-litellm@0.1.9` and its evidence before publish.

## Acceptance Criteria
- [ ] AC-1: Confirm `0.1.9` is available and all package metadata is consistent.
- [ ] AC-2: Confirm intended release scope contains only the ten declared task-owned files.
- [ ] AC-3: Re-run build, tests, pack dry-run, behavioral adversarial checks, and OpenCode 1.18.21 integration.
- [ ] AC-4: Confirm the governing evidence packet exists and maps AC-1 through AC-7 with retained logs.
- [ ] AC-5: Approve or reject npm publish readiness.

## Expected Evidence
- Signed Tech Lead review with publish gate decision.

## Acceptance Criteria Verification Map
- [ ] AC-1
  - **Method:** npm and manifest inspection
  - **Evidence:** signed handoff
- [ ] AC-2
  - **Method:** scoped diff review
  - **Evidence:** signed handoff
- [ ] AC-3
  - **Method:** independent verification
  - **Evidence:** signed handoff
- [ ] AC-4
  - **Method:** evidence audit
  - **Evidence:** signed handoff
- [ ] AC-5
  - **Method:** release gate decision
  - **Evidence:** signed handoff

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations
- NPM publish approved for exact version `0.1.9` and the declared ten-file scope.
- Unrelated dirty and untracked files must remain excluded.
- Any materially different tarball requires rereview.
