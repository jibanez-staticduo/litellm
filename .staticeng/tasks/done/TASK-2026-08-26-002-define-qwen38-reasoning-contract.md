---
id: TASK-2026-08-26-002-define-qwen38-reasoning-contract
complexity: standard
track: spec
slice: foundation
status: done
scr: SCR-2026-08-26-001-qwen38-native-reasoning-modes
parent: null
assigned_to: technical_architect
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-26-002 - Define Qwen3.8 Reasoning Contract

## Objective
Create the unambiguous steady-state Qwen3.8 reasoning contract for both proxies and local clients.

## Acceptance Criteria
- [x] AC-1: Record exact NAS/Fedora route predicates and the single configured alias.
- [x] AC-2: Define visible modes `off`, `low`, `medium`, `xhigh`, omission/default behavior, and rejected values.
- [x] AC-3: Define direct Chat/Responses normalization, final-payload conflict semantics, and zero-forward rejection.
- [x] AC-4: Define plugin/OpenCode/Codex representations without contradicting public-versus-wire semantics.
- [x] AC-5: Define verification, rollout, rollback, privacy, and documentation gates preserving DeepSeek/unrelated behavior.

## Expected Evidence
- `.staticeng/docs/architecture/qwen38-reasoning-contract.md` linked from the SCR and implementation tasks.

## Acceptance Criteria Verification Map
- [x] AC-1
  - **Method:** architecture review against approved SCR and completed route mapping
  - **Evidence:** `.staticeng/docs/architecture/qwen38-reasoning-contract.md`, Target identity and route predicates
- [x] AC-2
  - **Method:** live CachyOS template/probe evidence review
  - **Evidence:** `.staticeng/docs/architecture/qwen38-reasoning-contract.md`, Public modes and defaults
- [x] AC-3
  - **Method:** endpoint and policy contract review
  - **Evidence:** `.staticeng/docs/architecture/qwen38-reasoning-contract.md`, Final-payload normalization and conflicts; Rejection contract
- [x] AC-4
  - **Method:** client boundary compatibility review
  - **Evidence:** `.staticeng/docs/architecture/qwen38-reasoning-contract.md`, Surface representations
- [x] AC-5
  - **Method:** operational and regression-isolation review
  - **Evidence:** `.staticeng/docs/architecture/qwen38-reasoning-contract.md`, Verification gates through Documentation obligations

# Post Implementation Task Updates

## Technical Architect: Post Implementation Expectations
- AC-1 through AC-5 are satisfied by the steady-state contract and signed handoff dated 2026-08-26
- Implementation tasks must link the approved SCR and `.staticeng/docs/architecture/qwen38-reasoning-contract.md`
- Public values remain exactly `off`, `low`, `medium`, and `xhigh`; direct public `off` reaches LiteLLM unchanged and LiteLLM emits `chat_template_kwargs.enable_thinking=false`
- Both proxies reject public `none` and `high` before forwarding; no private OpenCode or Codex alias is authorized without a future approved SCR amendment and trusted-boundary design
- Implementers must preserve exact per-deployment predicates, final-payload conflict rejection, zero-forward failures, rollout order, privacy controls, DeepSeek behavior, and client compatibility stop conditions
- No source code, runtime configuration, client configuration, or service was changed by this spec task
- Architecture review note: approved for decomposition and implementation subject to every verification and compatibility gate in the contract
- StaticEng validation and repair dry-run were run; documentation changes are structurally valid, but repository-wide validation remains blocked by pre-existing missing CodeMaps outside this documentation-only task
