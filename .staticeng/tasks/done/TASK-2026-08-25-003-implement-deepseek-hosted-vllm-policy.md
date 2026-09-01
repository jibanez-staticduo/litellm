---
id: TASK-2026-08-25-003-implement-deepseek-hosted-vllm-policy
complexity: complex
track: implementation
slice: logic
status: done
scr: SCR-2026-08-25-001-deepseek-v4-native-reasoning-modes
parent: null
assigned_to: developer
handoff_from: product_manager
reopened_count: 2
---

# Task: TASK-2026-08-25-003 - Implement DeepSeek Hosted-vLLM Policy

## Objective
Enforce the approved DeepSeek V4 native reasoning contract in LiteLLM's `hosted_vllm` transformation for both target aliases without changing unrelated models.

## Governing Contract
- `.staticeng/docs/architecture/deepseek-v4-reasoning-contract.md`
- `.staticeng/docs/scrs/SCR-2026-08-25-001-deepseek-v4-native-reasoning-modes.md`

## Acceptance Criteria
- [ ] AC-1: For resolved upstream `deepseek-ai/DeepSeek-V4-Flash`, accept omitted effort plus explicit public values `off`, `low`, `high`, and `max` only.
- [ ] AC-2: Translate `off` and `thinking.type=disabled` to one canonical upstream non-thinking control; pass `low`, `high`, and `max` exactly.
- [ ] AC-3: Reject `medium`, `xhigh`, and every other supplied unsupported value with deterministic HTTP 400-compatible model-specific errors before transport.
- [ ] AC-4: Apply the same policy to Chat Completions and Responses requests bridged through chat completions.
- [ ] AC-5: Preserve all existing behavior for unrelated hosted-vLLM models and all non-reasoning parameters.
- [ ] AC-6: Add focused regression tests proving accepted mappings, rejected values, no upstream forwarding on rejection where testable, omission behavior, and unrelated-model invariants.
- [ ] AC-7: Update relevant technical docs/CodeMaps only as required and produce complete evidence.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-25-003-implement-deepseek-hosted-vllm-policy/` with:
- `SUMMARY.md` mapping AC-1 through AC-7 to results.
- `logs/` containing focused test, lint/type, and diff-check outputs.

## Acceptance Criteria Verification Map
- [ ] AC-1
  - **Method:** unit tests
  - **Evidence:** evidence logs and summary
- [ ] AC-2
  - **Method:** transformation payload assertions
  - **Evidence:** evidence logs and summary
- [ ] AC-3
  - **Method:** negative unit tests
  - **Evidence:** evidence logs and summary
- [ ] AC-4
  - **Method:** Responses bridge regression test
  - **Evidence:** evidence logs and summary
- [ ] AC-5
  - **Method:** unrelated hosted-vLLM regression tests
  - **Evidence:** evidence logs and summary
- [ ] AC-6
  - **Method:** focused test suite
  - **Evidence:** evidence logs and summary
- [ ] AC-7
  - **Method:** documentation and evidence review
  - **Evidence:** task and evidence packet

## Reopen History

### Reopen 1 - 2026-08-25
- Tech Lead rejected deployment readiness because Chat and native Responses merge `extra_body` after transformation validation.
- Reproduced bypasses forward forbidden `reasoning_effort=medium` and `reasoning.effort=medium` values to transport.
- Required correction: enforce the contract against the final merged outbound payload or validate every supported source with explicit conflict precedence.
- Required tests: Chat and Responses transport-level zero-forwarding for sync/async or streaming paths, including `extra_body` injection and override conflicts.

### Reopen 2 - 2026-08-25
- Tech Lead confirmed the original Chat and nested Responses bypasses are fixed, but found a native Responses compatibility-field bypass.
- `extra_body={"reasoning_effort":"medium"}` survives finalization because the Responses policy inspects only nested `reasoning.effort`.
- Required correction: resolve nested `reasoning.effort` and top-level compatibility `reasoning_effort` using deterministic existing precedence or conflict semantics, then validate the authoritative value before transport.
- Required tests: sync/async and streaming/non-streaming zero-forwarding for compatibility-only invalid values, mixed valid/invalid conflicts in both directions, equal valid dual representations, and unrelated-model pass-through.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

- AC-1 through AC-7 are implemented for the scoped LiteLLM source, tests, docs, and CodeMaps
- The shared policy requires the exact resolved model group and exact upstream served identity, normalizes `off` and disabled thinking to `none`, and rejects all other supplied unsupported values before transport
- Focused verification passes with 42 tests, Ruff, shared-policy basedpyright, and `git diff --check`; evidence is under `.staticeng/evidences/TASK-2026-08-25-003-implement-deepseek-hosted-vllm-policy/`
- No deployment, OpenCode, plugin, or Codex configuration was changed. Nothing was staged or committed
- PMA should route the implementation and evidence packet to technical review before any rollout slice

## Developer: Reopen 1 Post Implementation Expectations

- Chat and native Responses now enforce the DeepSeek contract against the final merged outbound payload after `extra_body`, using a generic no-op provider finalization hook and target-specific hosted-vLLM overrides
- Existing `extra_body` precedence is preserved, but any final target reasoning value must be one of the approved public values before normalization and transport
- Transport-level tests prove zero upstream calls for sync and async Chat and Responses, with streaming and non-streaming requests, direct injection, and override conflicts
- Focused verification now passes with 53 tests, Ruff, shared-policy basedpyright, and `git diff --check`; existing evidence logs and summary were refreshed
- No deployment, OpenCode, plugin, or Codex configuration was changed. Nothing was staged or committed

## Developer: Reopen 2 Post Implementation Expectations

- Native Responses finalization now validates top-level compatibility `reasoning_effort` as well as nested `reasoning.effort`
- One representation is authoritative when supplied alone; equal dual representations are accepted and canonicalized to nested `reasoning.effort`; conflicting dual representations reject explicitly without silently choosing either value
- The requested compatibility-only invalid, valid-nested/invalid-top-level, invalid-nested/valid-top-level, equal-valid dual, and unrelated-model pass-through cases are covered across sync/async and stream/non-stream transport paths
- Rejected cases assert zero upstream calls. Focused verification passes with 59 tests, Ruff, shared-policy basedpyright, and `git diff --check`
- No deployment, image build, staging, OpenCode, plugin, or Codex configuration work occurred. Nothing was staged or committed
