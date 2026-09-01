---
id: TASK-2026-08-26-005-plugin-only-deepseek-qwen38-config
complexity: complex
track: implementation
slice: core
status: active
scr: SCR-2026-08-26-001-qwen38-native-reasoning-modes
parent: null
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-26-005 - Plugin-Only DeepSeek and Qwen3.8 Config

## Objective
Use only `opencode-litellm` generated configuration with official OpenCode 1.18.23 to expose the correct named thinking levels for DeepSeek and Qwen3.8.

## Constraints
- Never edit, build, replace, or patch OpenCode core/binaries.
- Never add manual DeepSeek/Qwen3.8 variant maps to `opencode.json`.
- LiteLLM remains generic pass-through; no model-specific proxy deployment.
- Final activation must use a published npm package reference; local `file://` references are prohibited in Syncthing-shared config.

## Acceptance Criteria
- [ ] AC-1: DeepSeek exact aliases generate named variants `off`, `low`, `high`, `max`; off serializes as serving-compatible `none`.
- [ ] AC-2: Qwen3.8 alias generates named variants `off`, `low`, `medium`, `xhigh`; off serializes as serving-compatible non-thinking control and native efforts remain exact.
- [ ] AC-3: Plugin tombstones remove unsupported generated named variants where official OpenCode merge semantics permit; no manual config is used.
- [ ] AC-4: Preserve all unrelated model mappings and overrides.
- [ ] AC-5: Validate official OpenCode 1.18.23 resolved config and strict-loopback request bodies for every mode.
- [ ] AC-6: Update tests/docs/dist/evidence and prepare local activation through the existing `file://` plugin reference only.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-26-005-plugin-only-deepseek-qwen38-config/` with `SUMMARY.md` and redacted logs.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

- Implemented the plugin-only generated configuration in `/home/staticduo/git/opencode-litellm`.
- Verified all ACs with unit tests, official OpenCode 1.18.23 isolated resolution, and twelve strict loopback captures.
- Qwen `off` uses `chat_template_kwargs.enable_thinking=false` directly; it does not expose or transmit unsupported `none`.
- Official 1.18.23 retains intrinsic `Predeterminado`; named tombstones cannot remove it under the supported plugin/config API.
- Release candidate is `@staticeng/opencode-litellm@0.1.9`; registry latest remains `0.1.8`, and the renewed 0.1.9 artifact contains only publish-intended files.
- Shared configuration must use pinned published npm and must never use a local path or `file://` reference.
- No production, publication, commit, push, active-config, or OpenCode-core action was performed.
