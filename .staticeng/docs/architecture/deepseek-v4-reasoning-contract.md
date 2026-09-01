# DeepSeek V4 Reasoning Contract

## Status and scope

This is the steady-state technical contract for
`SCR-2026-08-25-001-deepseek-v4-native-reasoning-modes`. It governs the two
LiteLLM deployments, `opencode-litellm`, local OpenCode, and local Codex. It
does not change the reasoning contract of any unrelated model

The deployed checkpoint is `deepseek-ai/DeepSeek-V4-Flash-0731`. vLLM keeps
the served model identity `deepseek-ai/DeepSeek-V4-Flash`, and LiteLLM keeps
the public model group `deepseek-v4-flash-fp8-mtp`

## Target identity

The target predicate is true only when both of these exact conditions hold:

1. The resolved LiteLLM model group is exactly
   `deepseek-v4-flash-fp8-mtp`
2. The resolved upstream model, after removing exactly one transport provider
   prefix `hosted_vllm/` when present, is exactly
   `deepseek-ai/DeepSeek-V4-Flash`

Matching is case-sensitive. Substring, suffix, checkpoint-name, `base_model`,
display-name, and one-sided matches do not satisfy the predicate. The
checkpoint name is deployment documentation, not an alternate request or
routing identity

Validation must run after route resolution has made both identities available
and before any network call to vLLM. This prevents a public alias alone or an
upstream identity alone from changing behavior for another route

## Public modes and normalization

For a supplied reasoning mode on the target, the public enum is exactly:

| Public mode | Canonical LiteLLM value forwarded to vLLM |
| --- | --- |
| `off` | `reasoning_effort=none` |
| `low` | `reasoning_effort=low` |
| `high` | `reasoning_effort=high` |
| `max` | `reasoning_effort=max` |

`low`, `high`, and `max` are exact pass-through values. `off` is the only
translation. The private canonical value `none` must not be exposed as a fifth
public mode

Omitting the reasoning field is allowed and leaves existing deployment
defaults intact. Supplying null, an empty string, a differently cased value,
`medium`, `xhigh`, `none`, or any other value is unsupported for the target

## Rejection contract

Unsupported supplied values for the target must fail deterministically before
forwarding. The failure must use LiteLLM's existing invalid-request contract,
identify the invalid value and target model group, and list the allowed public
values `off`, `low`, `high`, and `max`. It must not silently drop, clamp,
translate, or retry the request

The same policy applies to streaming and non-streaming requests. A rejected
request must produce no upstream attempt. Validation and translation must be
shared by Chat Completions and Responses instead of duplicated as divergent
endpoint policy

When the target predicate is false, the guard is a no-op. Existing accepted
values, translations, defaults, errors, and forwarding behavior for every
unrelated model remain unchanged

## Surface representations

### Chat Completions

Clients send the public value as top-level `reasoning_effort`:

```json
{
  "model": "deepseek-v4-flash-fp8-mtp",
  "reasoning_effort": "off"
}
```

After target validation, LiteLLM forwards `reasoning_effort: "none"` for
`off`, or the exact `low`, `high`, or `max` value

### Responses

Clients send the public value in the OpenAI-compatible reasoning object:

```json
{
  "model": "deepseek-v4-flash-fp8-mtp",
  "reasoning": {
    "effort": "off"
  }
}
```

LiteLLM extracts `reasoning.effort` into the shared target policy before the
completion bridge or provider transform. The canonical forwarded control is
the same `reasoning_effort` value defined in the normalization table. If both
`reasoning.effort` and a compatibility `reasoning_effort` are supplied, the
request must follow the existing LiteLLM conflict or precedence contract
before target validation; the target policy must never choose between two
different caller values silently

### `opencode-litellm` legacy provider

For the exact target identity, generated legacy model metadata contains
`reasoning: true` and exactly these variants:

```json
{
  "off": { "reasoningEffort": "none" },
  "low": { "reasoningEffort": "low" },
  "high": { "reasoningEffort": "high" },
  "max": { "reasoningEffort": "max" }
}
```

Generation is target-specific and must not alter generic reasoning variants or
overrides for unrelated models

### `opencode-litellm` V2 provider

The V2 model has `capabilities.reasoning: true` and exactly this ordered
variant list:

```json
[
  { "id": "off", "body": { "reasoning_effort": "none" } },
  { "id": "low", "body": { "reasoning_effort": "low" } },
  { "id": "high", "body": { "reasoning_effort": "high" } },
  { "id": "max", "body": { "reasoning_effort": "max" } }
]
```

The plugin keeps `off` as the user-visible variant ID but serializes its request
body with the private wire value `none`. This client-adapter normalization is
required because OpenCode uses the variant body directly as provider request
options. Direct LiteLLM callers may still send public `off`; LiteLLM owns
validation and normalization for those direct API requests

### OpenCode

OpenCode consumes the variants generated by `opencode-litellm`. Local
`opencode.json` must not define a manual variant map for the target because
provider or model overrides can replace or merge into generated metadata and
reintroduce unsupported modes. Selection of `off`, `low`, `high`, or `max`
must produce the corresponding plugin request body unchanged. Therefore visible
`off` sends private wire `none`, while the three native values remain exact

### Codex

The target entry in the local Codex model catalog uses
`default_reasoning_level` set to one supported public value and
`supported_reasoning_levels` containing exactly `off`, `low`, `high`, and
`max`. When the target is active, `model_reasoning_effort` must also be one of
those values. With `wire_api = "responses"`, Codex must transmit the selected
public value unchanged as `reasoning.effort`; LiteLLM then owns validation and
normalization

Codex has a mandatory compatibility stop condition: do not deploy the Codex
catalog or config slice unless the installed Codex version can parse, display
or select, persist, and transmit both `off` and `max` unchanged on the
Responses wire path. If any stage rejects, hides, aliases, or rewrites either
value, stop before modifying active Codex configuration and return the slice
to PMA for a client-adapter or Codex-version decision. Do not substitute
`none`, `medium`, or `xhigh`

## Verification gates

Implementation is complete only when all applicable gates pass on both
LiteLLM deployments:

1. Unit or contract tests prove exact two-part identity matching, all four
   accepted mappings, omission behavior, deterministic rejection of
   `medium`, `xhigh`, `none`, null, case variants, and an arbitrary unknown
   value, plus no behavior change for near-match and unrelated models
2. Chat Completions and Responses tests cover streaming and non-streaming
   requests and prove rejected requests make zero upstream calls
3. A controlled vLLM probe proves `none`, `low`, `high`, and `max` are accepted
   canonical upstream controls before either deployment is changed
4. Plugin tests snapshot the exact legacy object and V2 ordered list, and
   prove unrelated model mappings remain unchanged
5. OpenCode inspection and a request capture prove there is no conflicting
   manual target override and each generated variant reaches LiteLLM unchanged
6. Codex compatibility tests satisfy the stop condition before configuration
   rollout, followed by catalog inspection and a Responses request capture for
   every mode
7. Live positive and negative probes pass through each public LiteLLM endpoint,
   with service health checked before and after rollout

Evidence must record versions, redacted requests, status and error bodies,
upstream request captures, test commands, and rollback decisions. It must map
each result to the implementation task's numbered acceptance criteria

## Rollout and rollback

Roll out in dependency order: shared LiteLLM policy and endpoint integration,
first LiteLLM deployment, second LiteLLM deployment, plugin, OpenCode, then
Codex. Do not expose generated client modes before both proxies enforce the
contract. Validate each boundary before advancing

Each slice must preserve a dated, secret-free backup or a versioned prior
artifact and document its exact reversal. Rollback is boundary-local:

- LiteLLM: restore the prior code or package and restart only the affected
  deployment
- Plugin: restore the prior published or installed plugin version
- OpenCode: remove target-specific local overrides and restore the prior plugin
  lock/config artifact
- Codex: restore the prior catalog and config together

Any forwarding of a rejected value, unrelated-model regression, target
identity mismatch, mode rewrite, failed health check, or failed Codex stop
condition halts rollout. Roll back the current boundary before proceeding

## Privacy and observability

Logs and evidence may include the model group, normalized mode, endpoint,
status, deployment identifier, and correlation identifier. They must not
include API keys, authorization headers, cookies, prompts, completion text,
tool arguments, full request bodies, or unredacted environment/config dumps

Invalid-value logging must use a bounded or safely escaped representation so a
caller-controlled value cannot inject logs or create unbounded records. Normal
reasoning mode selection does not require prompt or response-content logging

## Documentation obligations

Implementation tasks must link this contract and the approved SCR. Any change
to the target identity, public enum, translation, rejection semantics, surface
representation, or Codex stop condition requires an approved SCR update before
implementation. Deployment runbooks must identify the served alias and actual
`DeepSeek-V4-Flash-0731` checkpoint without treating the checkpoint as a
public request identity
## 2026-08-26 Client-Owned Scope Override

The approved SCR now supersedes this document's proxy-enforcement requirements. LiteLLM remains a generic pass-through and does not enforce a DeepSeek-specific effort allowlist. OpenCode and Codex own the selectable set `off`, `low`, `high`, `max` and correct request serialization. The task-owned LiteLLM policy described here must not be deployed.
