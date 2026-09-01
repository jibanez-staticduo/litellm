---
id: TASK-2026-08-26-003-remove-unused-litellm-reasoning-policy
complexity: standard
track: implementation
slice: logic
status: todo
scr: SCR-2026-08-25-001-deepseek-v4-native-reasoning-modes
parent: null
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-26-003 - Remove Unused LiteLLM Reasoning Policy

## Objective
Remove only the uncommitted task-owned DeepSeek/Qwen model-specific LiteLLM enforcement work now superseded by client-owned validation, preserving every unrelated user/worktree change.

## Acceptance Criteria
- [ ] AC-1: Identify the exact task-owned LiteLLM source/test/CodeMap diff from tasks 003-007.
- [ ] AC-2: Remove only those model-specific validation/finalizer changes; preserve unrelated changes in shared files.
- [ ] AC-3: Restore existing generic hosted-vLLM pass-through behavior and run focused baseline tests.
- [ ] AC-4: Do not build/deploy/restart either LiteLLM proxy.
- [ ] AC-5: Produce evidence and a scoped diff proving no unrelated reversion.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-26-003-remove-unused-litellm-reasoning-policy/` with `SUMMARY.md` and logs.
