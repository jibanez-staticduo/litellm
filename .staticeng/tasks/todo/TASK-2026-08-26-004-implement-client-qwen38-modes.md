---
id: TASK-2026-08-26-004-implement-client-qwen38-modes
complexity: complex
track: implementation
slice: core
status: todo
scr: SCR-2026-08-26-001-qwen38-native-reasoning-modes
parent: null
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-26-004 - Implement Client Qwen3.8 Modes

## Objective
Extend the approved `opencode-litellm` and OpenCode client mechanism to `qwen3.8-27b-refusal-dial`, exposing only Off, Low, Medium, XHigh and serializing valid serving controls.

## Acceptance Criteria
- [ ] AC-1: Plugin generates exact Qwen3.8 visible variants and suppresses generic/default unsupported variants.
- [ ] AC-2: Off serializes to a vLLM-compatible non-thinking request; low/medium/xhigh remain exact.
- [ ] AC-3: Reuse the approved OpenCode model-scoped default suppression without broadening unrelated behavior.
- [ ] AC-4: Preserve DeepSeek exact Off/Low/High/Max behavior.
- [ ] AC-5: Add tests and strict-loopback captures for both models and all modes.
- [ ] AC-6: Produce evidence and prepare build/local activation without npm publication dependency.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-26-004-implement-client-qwen38-modes/` with `SUMMARY.md`, logs, and UI screenshots when activated.
