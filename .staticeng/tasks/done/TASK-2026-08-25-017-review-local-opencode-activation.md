---
id: TASK-2026-08-25-017-review-local-opencode-activation
complexity: standard
track: investigation
slice: qa
status: done
scr: SCR-2026-08-25-001-deepseek-v4-native-reasoning-modes
parent: TASK-2026-08-25-016-activate-local-opencode-deepseek-variants
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-25-017 - Review Local OpenCode Activation

## Objective
Independently verify the local OpenCode activation, review the disclosed isolation incident, and decide closure readiness.

## Acceptance Criteria
- [ ] AC-1: Confirm active config changed only the plugin reference and retains mode `0600` with a valid owner-only rollback backup.
- [ ] AC-2: Confirm both aliases expose exactly `off`, `low`, `high`, and `max` with no manual override.
- [ ] AC-3: Independently capture all four sanitized request efforts using strict loopback isolation and prove no production endpoint is reachable from the harness.
- [ ] AC-4: Review available logs for the initial accidental production `off` request and confirm rejection before inference with no completion.
- [ ] AC-5: Approve closure or return task 016 for correction.

## Expected Evidence
- Signed Tech Lead review and closure decision.

## Acceptance Criteria Verification Map
- [ ] AC-1
  - **Method:** config and backup inspection
  - **Evidence:** signed handoff
- [ ] AC-2
  - **Method:** OpenCode model inspection
  - **Evidence:** signed handoff
- [ ] AC-3
  - **Method:** isolated loopback capture
  - **Evidence:** signed handoff
- [ ] AC-4
  - **Method:** incident evidence review
  - **Evidence:** signed handoff
- [ ] AC-5
  - **Method:** closure gate
  - **Evidence:** signed handoff

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations
- Closure rejected on 2026-08-25.
- Task 016 reopened for a repeatable no-external-network capture harness and corrected incident wording.
