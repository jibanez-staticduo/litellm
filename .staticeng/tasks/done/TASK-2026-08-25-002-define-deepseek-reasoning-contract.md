---
id: TASK-2026-08-25-002-define-deepseek-reasoning-contract
complexity: standard
track: spec
slice: foundation
status: done
scr: SCR-2026-08-25-001-deepseek-v4-native-reasoning-modes
parent: null
assigned_to: technical_architect
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-25-002 - Define DeepSeek Reasoning Contract

## Objective
Create the steady-state technical contract governing DeepSeek V4 reasoning modes across LiteLLM, `opencode-litellm`, OpenCode, and Codex.

## Acceptance Criteria
- [x] AC-1: Define the exact target identity predicate for public group `deepseek-v4-flash-fp8-mtp` and upstream `deepseek-ai/DeepSeek-V4-Flash`, documented as the deployed `DeepSeek-V4-Flash-0731` checkpoint.
- [x] AC-2: Define the public enum as exactly `off`, `low`, `high`, and `max`; define `off -> reasoning_effort=none` and exact pass-through for the other three.
- [x] AC-3: Require deterministic pre-forward rejection of `medium`, `xhigh`, and every unsupported value for the target while preserving unrelated model behavior.
- [x] AC-4: Define Chat Completions, Responses, plugin legacy/V2, OpenCode, and Codex representations plus the Codex stop condition.
- [x] AC-5: Record verification, rollback, privacy, and documentation requirements for implementation slices.

## Expected Evidence
- A reviewed steady-state technical contract under `.staticeng/docs/` linked from the SCR and implementation task files.

## Acceptance Criteria Verification Map
- [x] AC-1
  - **Method:** architecture review
  - **Evidence:** `.staticeng/docs/architecture/deepseek-v4-reasoning-contract.md`, Target identity
- [x] AC-2
  - **Method:** official documentation and direct vLLM probe review
  - **Evidence:** `.staticeng/docs/architecture/deepseek-v4-reasoning-contract.md`, Public modes and normalization
- [x] AC-3
  - **Method:** policy review
  - **Evidence:** `.staticeng/docs/architecture/deepseek-v4-reasoning-contract.md`, Rejection contract
- [x] AC-4
  - **Method:** client compatibility review
  - **Evidence:** `.staticeng/docs/architecture/deepseek-v4-reasoning-contract.md`, Surface representations
- [x] AC-5
  - **Method:** operational review
  - **Evidence:** `.staticeng/docs/architecture/deepseek-v4-reasoning-contract.md`, Verification gates through Documentation obligations

# Post Implementation Task Updates

## Technical Architect: Post Implementation Expectations
- AC-1 through AC-5 are satisfied by the steady-state contract and signed handoff dated 2026-08-25
- Implementation tasks must link the approved SCR and `.staticeng/docs/architecture/deepseek-v4-reasoning-contract.md`
- Implementers must preserve the exact two-part target predicate, target-only rejection policy, endpoint and client representations, rollout order, privacy controls, and Codex compatibility stop condition
- No implementation code, runtime configuration, client configuration, or service was changed by this spec task
- Architecture review note: approved for decomposition and implementation, subject to the Codex stop condition and per-boundary verification gates in the contract
- StaticEng validation was run; the contract and task introduced no reported error, but repository-wide validation remains blocked by pre-existing missing CodeMaps outside this task's documentation-only scope
