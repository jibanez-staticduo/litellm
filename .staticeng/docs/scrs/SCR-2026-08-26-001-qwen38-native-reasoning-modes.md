---
id: SCR-2026-08-26-001-qwen38-native-reasoning-modes
status: approved
requested_by: user
approved_by: user
date: 2026-08-26
---

# SCR: Qwen3.8 Native Reasoning Modes

## Requested Behavior
- For every configured Qwen3.8 model, expose only `off`, `low`, `medium`, and `xhigh` across both LiteLLM deployments, `opencode-litellm`, OpenCode, and Codex on this host.
- Reject unsupported effort values including `none`, `minimal`, `high`, and `max` instead of allowing vLLM's generic schema to pass them to the model template.
- Translate semantic `off` to `chat_template_kwargs.enable_thinking=false`; pass `low`, `medium`, and `xhigh` as exact native `reasoning_effort` values.
- Generate OpenCode variants through `opencode-litellm`; do not maintain manual Qwen3.8 variant lists.

## Acceptance Intent
- Scope is every currently configured Qwen3.8 alias whose resolved upstream checkpoint belongs to the Qwen3.8 family.
- Both LiteLLM proxies enforce the model-native contract before forwarding.
- OpenCode shows exactly Off, Low, Medium, XHigh with no default sentinel or unsupported generic variants.
- Codex exposes exactly the same four semantic modes for configured Qwen3.8 entries.
- Existing DeepSeek and unrelated model contracts remain unchanged.

## Verified Native Basis
- Live CachyOS model: `unsloth/Qwen3.8-27B-NVFP4`, served as `qwen3.8-27b-refusal-dial` on port 8083.
- Live template and probes accept `off` via `enable_thinking=false`, plus `low`, `medium`, and `xhigh`; `xhigh` is the default.
- Live template rejects `none`, `minimal`, `high`, and `max` despite vLLM's generic OpenAPI enum.

## Approval
Approved directly by the user on 2026-08-26.

## Scope Override - Client-Owned Validation
- Per user direction on 2026-08-26, LiteLLM does not need model-specific rejection or normalization for Qwen3.8.
- OpenCode and Codex own the selectable mode set and must send valid native controls.
- Do not implement or deploy a Qwen3.8-specific LiteLLM policy; preserve generic proxy behavior.
- Client-visible modes remain `off`, `low`, `medium`, `xhigh`; clients must serialize `off` using the serving-compatible non-thinking control.

## Scope Override - Official OpenCode Only
- Per explicit user correction on 2026-08-26, do not build, patch, or replace OpenCode core/binaries.
- Use only `opencode-litellm` generated configuration with the official OpenCode release.
- No manual Qwen3.8 variant map should be added to `opencode.json`.

## Scope Override - Published Plugin Only
- Syncthing-shared OpenCode configuration must use the published npm package, never a host-local `file://` path.
- Repository-local npm credentials may be used only for authenticated publication and must not be printed, copied to evidence, committed, or persisted in shared config.

## Steady-State Architecture
- The implementation source of truth is `.staticeng/docs/architecture/qwen38-reasoning-contract.md`
- Every implementation task must link both this approved SCR and the architecture contract
