---
id: TASK-2026-08-25-008-investigate-staging-auth-blocker
complexity: standard
track: investigation
slice: foundation
status: done

# Post Implementation Task Updates

## Technical Architect: Post Implementation Expectations
- ChatGPT reauthentication is not required.
- Use a temporary private verification stack backed by an immediately pruned clone of staging data.
- Preserve only both DeepSeek aliases and one provider-verified unrelated hosted-vLLM control model.
scr: SCR-2026-08-25-001-deepseek-v4-native-reasoning-modes
parent: TASK-2026-08-25-007-build-stage-deepseek-policy-image
assigned_to: technical_architect
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-25-008 - Investigate Staging Auth Blocker

## Objective
Identify the safest non-production way to make NAS staging healthy for DeepSeek policy verification without altering production credentials or requiring unnecessary ChatGPT authentication.

## Acceptance Criteria
- [ ] AC-1: Identify the exact staging startup wrapper, profile, and configuration path triggering ChatGPT reauthentication.
- [ ] AC-2: Determine whether staging can safely use an isolated test configuration/model subset while preserving the target DeepSeek aliases and one unrelated hosted-vLLM control model.
- [ ] AC-3: Propose the smallest reversible repair, explicitly excluding production credential mutation and secret disclosure.
- [ ] AC-4: Define verification and rollback steps and whether user-assisted reauthentication is truly required.

## Expected Evidence
- Signed read-only investigation handoff with redacted paths, commands, risks, and recommendation.

## Acceptance Criteria Verification Map
- [ ] AC-1
  - **Method:** staging configuration inspection
  - **Evidence:** signed handoff
- [ ] AC-2
  - **Method:** dependency and model-loading analysis
  - **Evidence:** signed handoff
- [ ] AC-3
  - **Method:** safety review
  - **Evidence:** signed handoff
- [ ] AC-4
  - **Method:** operational plan review
  - **Evidence:** signed handoff
