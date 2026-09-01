---
id: TASK-2026-08-25-012-review-opencode-litellm-deepseek-variants
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

# Task: TASK-2026-08-25-012 - Review opencode-litellm DeepSeek Variants

## Objective
Independently review the plugin implementation and prove OpenCode 1.18.21 resolves exactly the four approved DeepSeek variants without manual configuration.

## Acceptance Criteria
- [ ] AC-1: Confirm exact target scoping for both aliases and no near-match effects.
- [ ] AC-2: Confirm exact legacy/V2 payloads and authoritative post-merge enforcement.
- [ ] AC-3: Confirm `medium` and `xhigh` cannot survive provider/model overrides.
- [ ] AC-4: Independently run build/tests/package checks and OpenCode 1.18.21 config integration.
- [ ] AC-5: Approve or reject release/publish readiness with exact findings.

## Expected Evidence
- Signed Tech Lead review and release gate decision.

## Acceptance Criteria Verification Map
- [ ] AC-1
  - **Method:** code and test review
  - **Evidence:** signed handoff
- [ ] AC-2
  - **Method:** output assertions
  - **Evidence:** signed handoff
- [ ] AC-3
  - **Method:** adversarial override tests
  - **Evidence:** signed handoff
- [ ] AC-4
  - **Method:** independent verification
  - **Evidence:** signed handoff
- [ ] AC-5
  - **Method:** release gate decision
  - **Evidence:** signed handoff

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations
- Candidate behavior approved, but publish readiness rejected on 2026-08-25.
- Task 011 reopened for a new immutable npm version, complete evidence, and a clean intended release diff.
