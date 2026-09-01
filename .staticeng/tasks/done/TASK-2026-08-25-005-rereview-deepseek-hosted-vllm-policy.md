---
id: TASK-2026-08-25-005-rereview-deepseek-hosted-vllm-policy
complexity: standard
track: investigation
slice: qa
status: done
scr: SCR-2026-08-25-001-deepseek-v4-native-reasoning-modes
parent: TASK-2026-08-25-003-implement-deepseek-hosted-vllm-policy
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-25-005 - Rereview DeepSeek Hosted-vLLM Policy

## Objective
Verify the reopened implementation closes both `extra_body` bypasses and is safe for image build and staged deployment.

## Acceptance Criteria
- [ ] AC-1: Reproduce prior Chat and Responses bypass probes and confirm deterministic pre-transport rejection with zero upstream calls.
- [ ] AC-2: Confirm final-payload validation executes after `extra_body` merge in sync, async, streaming, and non-streaming paths.
- [ ] AC-3: Confirm `off`, `low`, `high`, `max`, omission, and unrelated-model behavior remain correct.
- [ ] AC-4: Independently run focused tests and inspect generic hook changes for regressions.
- [ ] AC-5: Approve or reject image build/staging readiness with exact findings.

## Expected Evidence
- Signed Tech Lead rereview using the shared output contract.

## Acceptance Criteria Verification Map
- [ ] AC-1
  - **Method:** transport-level regression probes
  - **Evidence:** signed handoff
- [ ] AC-2
  - **Method:** code-path review
  - **Evidence:** signed handoff
- [ ] AC-3
  - **Method:** focused test review
  - **Evidence:** signed handoff
- [ ] AC-4
  - **Method:** independent test execution
  - **Evidence:** signed handoff
- [ ] AC-5
  - **Method:** release gate decision
  - **Evidence:** signed handoff

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations
- Image build and staging readiness rejected on 2026-08-25.
- The original Chat and nested Responses bypasses are fixed.
- The Responses top-level compatibility `reasoning_effort` bypass must be corrected in reopened task 003.
