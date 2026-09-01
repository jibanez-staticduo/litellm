---
id: TASK-2026-08-25-001-map-deepseek-reasoning-surfaces
complexity: complex
track: investigation
slice: foundation
status: done
scr: SCR-2026-08-25-001-deepseek-v4-native-reasoning-modes
parent: null
assigned_to: technical_architect
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-25-001 - Map DeepSeek Reasoning Surfaces

## Objective
Map the exact implementation and deployment surfaces needed to enforce native DeepSeek V4 reasoning modes across both LiteLLM deployments, `opencode-litellm`, OpenCode, and Codex on this host.

## Acceptance Criteria
- [ ] AC-1: Identify exact repositories, files, services, versions, and current request transformations for all five surfaces.
- [ ] AC-2: Define a shared validation and translation contract that permits only `off`, `low`, `high`, and `max`, rejecting `medium` and `xhigh` only for the target DeepSeek model.
- [ ] AC-3: Decompose implementation into atomic, ordered slice tasks with tests, rollout checks, rollback points, and no conflicting shared-worktree edits.
- [ ] AC-4: State documentation impact and risks, including compatibility with current OpenCode and Codex schemas.

## Expected Evidence
- Read-only paths, symbols, configuration excerpts, and version outputs with secrets redacted.
- A proposed acceptance-criteria and verification map for each implementation slice.

## Acceptance Criteria Verification Map
- [ ] AC-1
  - **Method:** repository and deployment inspection
  - **Evidence:** signed technical architect handoff
- [ ] AC-2
  - **Method:** contract review against official DeepSeek and direct vLLM evidence
  - **Evidence:** signed technical architect handoff
- [ ] AC-3
  - **Method:** decomposition review
  - **Evidence:** signed technical architect handoff
- [ ] AC-4
  - **Method:** compatibility and documentation impact review
  - **Evidence:** signed technical architect handoff

# Post Implementation Task Updates

## Technical Architect: Post Implementation Expectations
- AC-1 through AC-4 are satisfied by the signed architecture handoff dated 2026-08-25.
- No implementation files or runtime services were changed during this investigation.
- The handoff identifies nine atomic slices, exact rollback points, and an explicit Codex compatibility stop condition.
