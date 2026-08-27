---
id: SCR-2026-08-26-002-client-model-contracts-020
status: approved
requested_by: user
approved_by: user
date: 2026-08-26
---

# SCR: Final Client Model Contracts in opencode-litellm 0.2.2

## Normative Steady State

This section is authoritative. Later sections preserve decision history only and do not modify this contract

- Published plugin: `@staticeng/opencode-litellm@0.2.2`, referenced by the exact unversioned string `@staticeng/opencode-litellm`
- Supported OpenCode runtime: official OpenCode `1.18.23`, without a core patch, fork, or local build
- Supported Codex runtime: Codex `0.149.1`, without a binary patch
- Retained client contract families: eight, comprising six GPT families, DeepSeek V4 Flash, and Qwen3.8
- Retired everywhere: normal GPT-5.3 Codex and GPT-5.3 Codex Spark, including exact routes, fallbacks, dependencies, shared overrides, OpenCode catalog visibility, and Codex rows
- Retired on NAS: `defend/gpt-5.5`, including its route, fallbacks, dependencies, and OpenCode override
- Official OpenCode's intrinsic `Default` or `Predeterminado` selector explicitly sends the official contract default and is not an additional named mode
- Explicit model and provider overrides apply last. Effective precedence is explicit user override over built-in contract over discovery

## Product Intent

- Keep one maintained internal source of truth in `opencode-litellm` for known model contracts
- Keep shared OpenCode configuration free of duplicated known-model capability tables
- Expose accurate selectors, defaults, and payloads in official OpenCode and Codex
- Preserve arbitrary expert overrides while using built-in contracts for normal operation
- Return ordinary unavailable-model behavior for retired aliases without redirecting them to another model

## Product Contract

### Terms

- **Named mode** means a user-selectable lowercase mode ID shown by OpenCode or Codex
- **Contract default** means the official mode sent when OpenCode's intrinsic default selector is used and the default recorded in the Codex catalog
- **Legacy wire** means the OpenCode legacy model variant object consumed as provider options
- **V2 wire** means the OpenCode V2 variant body
- **Codex wire** means `reasoning.effort` on the Responses API

### Complete Retained Contract Matrix

All mode lists are ordered and exhaustive. Values not listed for a row must not be generated as named modes

| Contract family | OpenCode named modes | Explicit OpenCode default | Legacy and V2 wire mapping | Codex 0.149.1 Responses modes |
| --- | --- | --- | --- | --- |
| GPT-5.4 | `none`, `low`, `medium`, `high`, `xhigh` | `none` | each ID maps unchanged through legacy `reasoningEffort` and V2 `reasoning_effort` | same five values, sent unchanged |
| GPT-5.4 Mini | `none`, `low`, `medium`, `high`, `xhigh` | `none` | same-name exact mapping | same five values, sent unchanged |
| GPT-5.5 | `none`, `low`, `medium`, `high`, `xhigh` | `medium` | same-name exact mapping | same five values, sent unchanged |
| GPT-5.6 Luna | `none`, `low`, `medium`, `high`, `xhigh`, `max` | `medium` | same-name exact mapping, including native `max` | same six values, sent unchanged |
| GPT-5.6 Sol | `none`, `low`, `medium`, `high`, `xhigh`, `max` | `medium` | same-name exact mapping, including native `max` | same six values, sent unchanged |
| GPT-5.6 Terra | `none`, `low`, `medium`, `high`, `xhigh`, `max` | `medium` | same-name exact mapping, including native `max` | same six values, sent unchanged |
| DeepSeek V4 Flash | `off`, `low`, `high`, `max` | `max` | visible `off` maps to wire `none`; all other values map unchanged | `none`, `low`, `high`, `max` |
| Qwen3.8 | `off`, `low`, `medium`, `xhigh` | `xhigh` | visible `off` maps only to `chat_template_kwargs.enable_thinking=false`; native values map unchanged | `low`, `medium`, `xhigh`; no Off |

`ultra` is outside this model-wire contract. It must not appear as an OpenCode variant or Codex catalog effort and must never be sent as raw `reasoning.effort`

### Exact Active Alias Classes

GPT contracts use exact membership, not substring, suffix, account-number, or base-model inference

| Model contract | In-scope aliases where the route exists |
| --- | --- |
| GPT-5.4 | `gpt-5.4`, `chatgpt/gpt-5.4`, `chatgpt-account2/gpt-5.4`, `chatgpt-account3/gpt-5.4` |
| GPT-5.4 Mini | `gpt-5.4-mini`, `chatgpt/gpt-5.4-mini`, `chatgpt-account2/gpt-5.4-mini`, `chatgpt-account3/gpt-5.4-mini` |
| GPT-5.5 | `gpt-5.5`, `chatgpt/gpt-5.5`, `chatgpt-account2/gpt-5.5`, `chatgpt-account3/gpt-5.5` |
| GPT-5.6 Luna | `gpt-5.6-luna`, `chatgpt/gpt-5.6-luna`, `chatgpt-account2/gpt-5.6-luna`, `chatgpt-account3/gpt-5.6-luna` |
| GPT-5.6 Sol | `gpt-5.6-sol`, `chatgpt/gpt-5.6-sol`, `chatgpt-account2/gpt-5.6-sol`, `chatgpt-account3/gpt-5.6-sol` |
| GPT-5.6 Terra | `gpt-5.6-terra`, `chatgpt/gpt-5.6-terra`, `chatgpt-account2/gpt-5.6-terra`, `chatgpt-account3/gpt-5.6-terra` |
| DeepSeek V4 Flash | exactly `deepseek-v4-flash-fp8-mtp` and `deepseek-v4-flash-fp8-mtp-norefusal` |
| Qwen3.8 | exactly `qwen3.8-27b-refusal-dial` |

An alias absent from discovery is not fabricated. A future alias, account namespace, checkpoint alias, near-match, or provider does not inherit a contract until an approved catalog change adds it explicitly

### Exact Retired Alias Classes

- Normal GPT-5.3 Codex: `gpt-5.3-codex`, `chatgpt/gpt-5.3-codex`, `chatgpt-account2/gpt-5.3-codex`, `chatgpt-account3/gpt-5.3-codex`
- GPT-5.3 Codex Spark: `gpt-5.3-codex-spark`, `chatgpt/gpt-5.3-codex-spark`, `chatgpt-account2/gpt-5.3-codex-spark`, `chatgpt-account3/gpt-5.3-codex-spark`
- Both families are absent from both LiteLLM registries, fallback/dependency state, OpenCode catalogs and overrides, and the NAS Codex custom catalog
- A request to any retired alias receives ordinary unavailable-model behavior with no deployment identity and no redirect

### Discovery, Built-in, and Override Precedence

The plugin resolves configuration in this order

1. LiteLLM discovery supplies the base model record and routability
2. The exact built-in contract supplies reasoning capability, ordered variants, wire bodies, explicit official default, and required compatibility metadata
3. Explicit model and provider overrides deep-merge last and may replace built-in or discovered fields; arrays and scalars retain the established replacement behavior
4. Generic shape normalization renders the final client configuration

Therefore precedence is **explicit user override over built-in contract over discovery**. Known models remain overrideable as an expert escape hatch, but the shipped shared configuration intentionally contains no known-model reasoning overrides. Unknown models retain the existing unrestricted override mechanism

### Shared OpenCode Configuration

- The plugin reference is exactly `@staticeng/opencode-litellm`, without a version suffix or `file://`; fresh reachable clients resolve published `0.2.2`
- The shared `overrides` object contains no active alias-table key, retired GPT-5.3 key, or `defend/gpt-5.5` key
- Unrelated override blocks and settings remain unchanged, including provider options, credential references, filters, non-LiteLLM providers, MCPs, model defaults, permissions, agents, and commands
- NAS is the sole direct writer. Syncthing distributes the authoritative mode-`0600` JSON to connected peers; offline peers converge when they reconnect

### Codex 0.149.1 Behavior

- The custom NAS Codex catalog has exactly eight retained rows in the matrix order and no normal or Spark GPT-5.3 row
- `supported_reasoning_levels` equals the ordered Codex subset in the matrix and `default_reasoning_level` equals the contract default
- The active `model_reasoning_effort`, when present, must be valid for the active model. A row switch must not leak a stale global effort
- Codex uses `wire_api = "responses"`; selected values follow the Codex column with no raw `ultra`, DeepSeek `off`, Qwen `off`, or substitution of `high` for Qwen `xhigh`
- The current active DeepSeek `high` selection is valid and remains unchanged. The generated model cache is not hand-edited

### Non-goals

- No OpenCode core/binary patch, fork, or local build
- No Codex binary patch
- No model-specific LiteLLM request validation, normalization, or allowlist
- No creation of aliases absent from discovery
- No change to routing priority, account fallback policy, authentication profiles, pricing, context limits, modalities, deployment topology, or provider credentials
- No redesign of generic unknown-model inference or override semantics
- No removal of unrelated OpenCode customization

## Numbered Acceptance Criteria

- **AC-1:** Plugin `0.2.2` recognizes every exact retained alias class, retires all eight exact normal/Spark GPT-5.3 aliases, does not match documented near-matches, and does not fabricate absent aliases
- **AC-2:** Generated OpenCode legacy and V2 metadata exposes exactly the ordered mode list and wire body in the retained matrix for every discovered in-scope alias
- **AC-3:** GPT-5.6 Luna, Sol, and Terra include native `max`; GPT-5.4, GPT-5.4 Mini, and GPT-5.5 do not; no retained contract exposes raw `ultra`
- **AC-4:** DeepSeek visible `off` serializes as wire `none`, Qwen visible `off` serializes only as `chat_template_kwargs.enable_thinking=false`, and all listed native values serialize unchanged
- **AC-5:** Discovery metadata that is absent, incomplete, or conflicting cannot remove or reorder built-in capability, modes, defaults, or wire mappings
- **AC-6:** Built-in contracts win over incomplete discovery; explicit model and provider overrides apply last for known and unknown models with the established replacement semantics
- **AC-7:** Official OpenCode `1.18.23` with plugin `0.2.2` shows only the retained named modes; its intrinsic default selector sends the explicit official contract default and is not counted as an additional named mode
- **AC-8:** Fresh reachable clients resolve the exact unversioned package reference to `0.2.2`; shared mode-`0600` JSON has no known/retired override or `file://` reference, preserves unrelated settings, and follows the approved connected-peer convergence scope
- **AC-9:** Normal and Spark GPT-5.3 are absent from both registries, fallbacks/dependencies, OpenCode catalogs/overrides, and the Codex catalog; `defend/gpt-5.5` is also absent from NAS; no retired alias redirects
- **AC-10:** Codex `0.149.1` exposes exactly eight retained rows with exact GPT lists/defaults, DeepSeek `none/low/high/max`, Qwen `low/medium/xhigh`, Responses wire behavior, no invalid Off or `ultra`, and a valid active effort
- **AC-11:** Redacted OpenCode captures prove every retained named mode, explicit official default, and exact wire payload for each distinct row; alias-equivalence covers every currently deployed exact alias
- **AC-12:** Redacted Codex captures prove every exposed effort for all eight rows plus row-switch no-leak behavior; unsupported labels are absent
- **AC-13:** Plugin build, 63/63 tests with zero skips, tracked-dist, package, official OpenCode, Codex, configuration, registry, and Syncthing gates pass with no required failure
- **AC-14:** Evidence maps AC-1 through AC-13, records versions and rollback sources, and contains no credentials, prompts, response content, authorization material, deployment identities, database payloads, or unredacted configuration

## Approval and Supersession History

The user approved the original contract on 2026-08-26, then approved the following corrections. These entries explain the path to the final state but are non-normative where they conflict with the normative sections above

- **Historical release baseline, superseded:** `0.2.0` was the planned release. Discovery-shape correction produced `0.2.1`, and Spark retirement produced the authoritative `0.2.2`
- **Historical Spark-preservation decision, superseded:** the original plan retained GPT-5.3 Codex Spark. On 2026-08-27 the user approved retiring Spark everywhere after official documentation and bounded live checks did not establish supported API operation
- **Historical default-omission wording, superseded:** earlier evidence expected omission of model-specific reasoning on OpenCode's intrinsic default selector. On 2026-08-27 the user approved explicit official-default transmission, which is the authoritative `0.2.2` behavior
- **Historical Codex baseline, superseded:** planning referenced Codex `0.147.0`. The authoritative runtime and all final gates use Codex `0.149.1`; historical 0.147 processes are not rollout gates
- **Connected-peer scope:** NAS is authoritative. Connected expected peers gate rollout; offline peers are not directly edited and converge automatically on reconnect
- **Release fallback:** trusted npm publishing repeatedly reached the registry but failed at the known PUT authorization step. The user-authorized protected credential fallback published each exact reviewed artifact without exposing credential material

## Final Evidence

- Task 004 proves plugin `0.2.2` publication, Spark removal from client catalogs, OpenCode `1.18.23` activation, and the final eight-row Codex `0.149.1` catalog
- Task 005 independently proves the retained selector/default/wire matrices and Fedora retirement state
- Task 019 proves final dual-registry normal/Spark retirement and NAS defend retirement
- Task 020 provides the complete final PASS trace for AC-1 through AC-14
