---
id: TASK-2026-08-25-018-review-opencode-core-fallback
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

# Task: TASK-2026-08-25-018 - Review OpenCode Core Fallback

## Objective
Independently review the plugin correction and minimal model-scoped OpenCode fallback before building or activating the modified UI/runtime.

## Acceptance Criteria
- [ ] AC-1: Confirm plugin exact aliases expose only `off`, `low`, `high`, and `max`, with tombstones preventing generic `medium`/`xhigh` and `off -> none` wire translation.
- [ ] AC-2: Confirm `variantDefault: false` is scoped, stripped before provider requests, and preserves default behavior for unrelated models.
- [ ] AC-3: Confirm both legacy and V2 prompt controls use the same resolver and render only Off/Low/High/Max for targets.
- [ ] AC-4: Independently run plugin and OpenCode focused tests plus strict-loopback captures for all four target modes and both aliases.
- [ ] AC-5: Review exact diffs for unrelated changes and approve or reject build/activation readiness.

## Expected Evidence
- Signed Tech Lead review and build/activation gate decision.

## Acceptance Criteria Verification Map
- [ ] AC-1
  - **Method:** plugin code/test review
  - **Evidence:** signed handoff
- [ ] AC-2
  - **Method:** OpenCode resolver/request review
  - **Evidence:** signed handoff
- [ ] AC-3
  - **Method:** UI component review/tests
  - **Evidence:** signed handoff
- [ ] AC-4
  - **Method:** independent test and capture execution
  - **Evidence:** signed handoff
- [ ] AC-5
  - **Method:** release gate decision
  - **Evidence:** signed handoff

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations
- Build and activation rejected on 2026-08-25.
- Task 011 reopened for default-sentinel semantics, provider scoping, preliminary-request investigation, and contract reconciliation.
