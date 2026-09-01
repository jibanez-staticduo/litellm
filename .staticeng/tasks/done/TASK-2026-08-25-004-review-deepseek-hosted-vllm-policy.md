---
id: TASK-2026-08-25-004-review-deepseek-hosted-vllm-policy
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

# Task: TASK-2026-08-25-004 - Review DeepSeek Hosted-vLLM Policy

## Objective
Independently review the LiteLLM DeepSeek V4 reasoning implementation, tests, and evidence before deployment.

## Acceptance Criteria
- [ ] AC-1: Confirm the diff matches the approved model-scoped contract with no unrelated behavior changes.
- [ ] AC-2: Confirm Chat and Responses mappings and rejection semantics are correct and cannot be bypassed through supported input shapes.
- [ ] AC-3: Confirm focused tests cover accepted, rejected, omitted, unrelated-model, and zero-forwarding behavior.
- [ ] AC-4: Re-run or inspect relevant verification and report any blocker with exact file/line references.
- [ ] AC-5: Approve deployment readiness or return the original implementation task for same-scope correction.

## Expected Evidence
- Signed Tech Lead review using the shared output contract.

## Acceptance Criteria Verification Map
- [ ] AC-1
  - **Method:** code review
  - **Evidence:** signed handoff
- [ ] AC-2
  - **Method:** transformation review
  - **Evidence:** signed handoff
- [ ] AC-3
  - **Method:** test review
  - **Evidence:** signed handoff
- [ ] AC-4
  - **Method:** independent verification
  - **Evidence:** signed handoff
- [ ] AC-5
  - **Method:** release gate decision
  - **Evidence:** signed handoff

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations
- Deployment readiness rejected on 2026-08-25.
- Chat and Responses `extra_body` bypasses must be corrected in the reopened original implementation task.
- Review evidence: focused tests passed but transport probes demonstrated forbidden values reaching upstream.
