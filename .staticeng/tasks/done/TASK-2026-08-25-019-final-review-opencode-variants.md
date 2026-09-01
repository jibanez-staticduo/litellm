---
id: TASK-2026-08-25-019-final-review-opencode-variants
complexity: standard
track: investigation
slice: qa
status: done

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations
- Functional review passed on 2026-08-25.
- Build/local activation rejected only pending documentation reconciliation.
scr: SCR-2026-08-25-001-deepseek-v4-native-reasoning-modes
parent: TASK-2026-08-25-011-implement-opencode-litellm-deepseek-variants
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-25-019 - Final Review OpenCode Variants

## Objective
Perform final independent review of the corrected plugin and OpenCode model-scoped variant behavior before build and local activation.

## Acceptance Criteria
- [ ] AC-1: Confirm target menus/current state/cycling expose only Off, Low, High, Max with no default, medium, or xhigh path.
- [ ] AC-2: Confirm unrelated models retain default and generic behavior.
- [ ] AC-3: Confirm plugin cleanup is scoped to LiteLLM provider plus exact aliases and off maps to wire none.
- [ ] AC-4: Independently run plugin/OpenCode focused tests and strict-loopback two-alias x four-mode captures with exactly eight user inference requests.
- [ ] AC-5: Confirm docs/evidence match the clarified contract and approve or reject build/local activation.

## Expected Evidence
- Signed Tech Lead final review and gate decision.

## Acceptance Criteria Verification Map
- [ ] AC-1
  - **Method:** UI state/cycle code and tests
  - **Evidence:** signed handoff
- [ ] AC-2
  - **Method:** non-regression tests
  - **Evidence:** signed handoff
- [ ] AC-3
  - **Method:** plugin code and request captures
  - **Evidence:** signed handoff
- [ ] AC-4
  - **Method:** independent verification
  - **Evidence:** signed handoff
- [ ] AC-5
  - **Method:** build gate decision
  - **Evidence:** signed handoff
