---
id: TASK-2026-08-25-006-final-review-deepseek-hosted-vllm-policy
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

# Task: TASK-2026-08-25-006 - Final Review DeepSeek Hosted-vLLM Policy

## Objective
Perform the final deployment-readiness review after the Responses compatibility-field correction.

## Acceptance Criteria
- [ ] AC-1: Confirm compatibility-only invalid values reject before transport.
- [ ] AC-2: Confirm unequal nested/top-level values reject, equal valid values canonicalize, and unrelated models pass through unchanged.
- [ ] AC-3: Re-run focused tests and adversarial transport probes across Chat and Responses.
- [ ] AC-4: Confirm no remaining supported input shape bypasses the target contract.
- [ ] AC-5: Approve or reject immutable image build and staging readiness.

## Expected Evidence
- Signed Tech Lead findings and gate decision.

## Acceptance Criteria Verification Map
- [ ] AC-1
  - **Method:** transport probes
  - **Evidence:** signed handoff
- [ ] AC-2
  - **Method:** payload and conflict tests
  - **Evidence:** signed handoff
- [ ] AC-3
  - **Method:** independent verification
  - **Evidence:** signed handoff
- [ ] AC-4
  - **Method:** adversarial review
  - **Evidence:** signed handoff
- [ ] AC-5
  - **Method:** release gate decision
  - **Evidence:** signed handoff

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations
- Approved immutable-image build and controlled staging deployment on 2026-08-25.
- Production remains gated on canonical upstream probes and staged positive/negative Chat and Responses checks.
