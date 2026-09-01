---
id: TASK-2026-08-26-023A-design-uvicorn-access-redaction
complexity: standard
track: spec
slice: logic
status: active
scr: null
parent: TASK-2026-08-26-023-fix-uvicorn-access-redaction
assigned_to: technical_architect
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-26-023A - Design Uvicorn access-log redaction fix

## Objective
Produce an implementation-ready design that preserves LiteLLM secret redaction and Uvicorn's structured access-record contract without changing source or runtime state.

## Acceptance Criteria
- [ ] AC-1: Map the relevant Python logging and Uvicorn `AccessFormatter` contracts, including supported `LogRecord.args` shapes and mutation risks.
- [ ] AC-2: Compare viable corrections and select the smallest secure approach, with explicit reasons for rejecting alternatives.
- [ ] AC-3: Specify exact production-code and mapped-test changes, including edge cases for tuple and mapping arguments and redaction failure behavior.
- [ ] AC-4: Define focused verification and deployment gates that prove no formatter traceback, no secret regression, and no request behavior change.

## Expected Evidence

Return a signed architecture handoff with exact source/test references and a stepwise implementation plan. This is a non-conflicting read-only spec task; do not edit implementation files, tests, deployment state, or other tasks.

## Acceptance Criteria Verification Map
- [ ] AC-1
  - **Method:** source and dependency contract inspection
  - **Evidence:** signed handoff
- [ ] AC-2
  - **Method:** option analysis
  - **Evidence:** signed handoff
- [ ] AC-3
  - **Method:** implementation design review
  - **Evidence:** signed handoff
- [ ] AC-4
  - **Method:** verification-plan review
  - **Evidence:** signed handoff

## Handoff
[Agent Message] From: product_manager To: technical_architect

Perform this read-only spec task while `TASK-2026-08-26-021A-review-release-021` remains the sole active shared-worktree implementation task. Use repository truth, inspect installed Uvicorn 0.51.0 behavior if useful, and return the shared output contract. Do not modify code, tests, dependencies, deployment, or StaticEng state.
