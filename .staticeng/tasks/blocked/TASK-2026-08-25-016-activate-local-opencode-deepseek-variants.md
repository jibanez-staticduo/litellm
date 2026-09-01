---
id: TASK-2026-08-25-016-activate-local-opencode-deepseek-variants
complexity: standard
track: implementation
slice: core
status: blocked
scr: SCR-2026-08-25-001-deepseek-v4-native-reasoning-modes
parent: TASK-2026-08-25-011-implement-opencode-litellm-deepseek-variants
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-25-016 - Activate Local OpenCode DeepSeek Variants

## Objective
Activate the reviewed `opencode-litellm` candidate locally so OpenCode 1.18.21 exposes exactly the four approved DeepSeek modes without manual model overrides while npm publication remains blocked.

## Acceptance Criteria
- [x] AC-1: Capture owner-only backup, checksum, permissions, installed plugin reference, and exact rollback.
- [x] AC-2: Point OpenCode to the reviewed local plugin artifact using a supported local plugin reference; do not add a manual DeepSeek model/variant override.
- [x] AC-3: Prove both target aliases resolve exactly `off`, `low`, `high`, and `max`; prove `medium` and `xhigh` are absent.
- [x] AC-4: Capture sanitized outgoing request bodies for all four modes and verify exact semantic efforts without sending prompts to production.
- [x] AC-5: Preserve every unrelated OpenCode setting/provider/model and file permission.
- [x] AC-6: Produce evidence and document the later one-line repin to npm `0.1.9` after publication.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-25-016-activate-local-opencode-deepseek-variants/` with `SUMMARY.md` and redacted logs.

## Acceptance Criteria Verification Map
- [x] AC-1
  - **Method:** baseline and backup inspection
  - **Evidence:** evidence packet
- [x] AC-2
  - **Method:** config diff
  - **Evidence:** evidence packet
- [x] AC-3
  - **Method:** OpenCode debug config/model inspection
  - **Evidence:** evidence packet
- [x] AC-4
  - **Method:** isolated loopback capture
  - **Evidence:** evidence packet
- [x] AC-5
  - **Method:** semantic config comparison
  - **Evidence:** evidence packet
- [x] AC-6
  - **Method:** closure review
  - **Evidence:** SUMMARY.md

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations

- Activated `file:///home/staticduo/git/opencode-litellm/dist/index.js` by changing only the existing plugin tuple reference
- Preserved the active config's owner-only `0600` permission and created an owner-only backup with matching baseline checksum
- Verified OpenCode 1.18.21 resolves exactly `off`, `low`, `high`, and `max` for both target aliases on legacy and V2 surfaces
- Captured eight sanitized successful request bodies through isolated loopback discovery and inference, proving each public effort reaches the provider unchanged
- Proved unrelated configuration semantic equality after normalizing the single approved plugin-reference change and confirmed no manual target override exists
- Recorded exact rollback and the future one-line npm repin to `@staticeng/opencode-litellm@0.1.9`
- No commit, publish, repository implementation edit, LiteLLM edit, Codex edit, or production inference was performed
- An initial production-directed request was rejected before inference due to incomplete config isolation; the retained successful verification uses isolated `XDG_CONFIG_HOME` and loopback only

## Reopen History

### Reopen 1 - 2026-08-25
- Independent review confirmed active config safety and exact variants but could not reproduce the eight request captures under strict network isolation.
- Build a self-contained reliable loopback harness inside an external-network-disabled namespace, capture both aliases x four modes, and record isolation proof.
- Correct incident evidence: the accidental production `off` request reached upstream vLLM schema validation, returned HTTP 400 before model generation, fallback was denied, and no completion was produced.

### Reopen 2 - 2026-08-25
- User-provided UI evidence disproves closure: OpenCode still shows generic `Predeterminado`, `Low`, `Medium`, `High`, `Max`, and `Off` instead of exactly the four contract variants.
- Selecting `Off` sends literal `reasoning_effort=off` to production, which vLLM rejects; the plugin must translate semantic `off` to the upstream non-thinking control.
- Activation remains blocked until the plugin/core integration produces an authoritative exact set and correct wire payloads in the real UI/runtime.
