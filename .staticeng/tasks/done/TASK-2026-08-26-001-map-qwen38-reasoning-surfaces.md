---
id: TASK-2026-08-26-001-map-qwen38-reasoning-surfaces
complexity: complex
track: investigation
slice: foundation
status: done

# Post Implementation Task Updates

## Technical Architect: Post Implementation Expectations
- Exactly one configured Qwen3.8 alias exists: `qwen3.8-27b-refusal-dial`.
- NAS resolves directly to CachyOS; Fedora chains through NAS.
- Implement only after active DeepSeek/OpenCode shared-worktree ownership is closed.
scr: SCR-2026-08-26-001-qwen38-native-reasoning-modes
parent: null
assigned_to: technical_architect
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-26-001 - Map Qwen3.8 Reasoning Surfaces

## Objective
Inventory every configured Qwen3.8 model and define the exact implementation/deployment plan for native reasoning alignment across both LiteLLM proxies, `opencode-litellm`, OpenCode, and local Codex.

## Acceptance Criteria
- [ ] AC-1: Identify every Qwen3.8 public alias, deployment ID, resolved upstream model, endpoint, and presence on NAS/Fedora LiteLLM.
- [ ] AC-2: Identify corresponding OpenCode/plugin and Codex entries plus current visible/default/wire modes.
- [ ] AC-3: Define an exact family predicate that includes configured Qwen3.8 models without matching Qwen3.5/3.6 or unrelated aliases.
- [ ] AC-4: Define Chat/Responses/client mappings for `off`, `low`, `medium`, and `xhigh`, and deterministic rejection of unsupported values.
- [ ] AC-5: Decompose atomic implementation, review, rollout, UI, and QA tasks with rollback points and no conflict with the active OpenCode build task.

## Expected Evidence
- Signed read-only architecture handoff with redacted paths, model identities, versions, and current behavior.

## Acceptance Criteria Verification Map
- [ ] AC-1
  - **Method:** live registry inspection
  - **Evidence:** signed handoff
- [ ] AC-2
  - **Method:** client/config inspection
  - **Evidence:** signed handoff
- [ ] AC-3
  - **Method:** identity design review
  - **Evidence:** signed handoff
- [ ] AC-4
  - **Method:** native template/API review
  - **Evidence:** signed handoff
- [ ] AC-5
  - **Method:** decomposition review
  - **Evidence:** signed handoff
