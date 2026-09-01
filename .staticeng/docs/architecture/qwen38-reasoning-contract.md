# Qwen3.8 Reasoning Contract

## Status and scope

This is the steady-state technical contract for
`SCR-2026-08-26-001-qwen38-native-reasoning-modes`. It governs the NAS and
Fedora LiteLLM deployments, `opencode-litellm`, local OpenCode, and local
Codex. It does not change the DeepSeek V4 contract or any unrelated model

The only configured Qwen3.8 public model group is
`qwen3.8-27b-refusal-dial`. NAS routes that group directly to the CachyOS
vLLM deployment on port 8083. Fedora routes the same group through NAS. The
CachyOS checkpoint is `unsloth/Qwen3.8-27B-NVFP4`, and vLLM serves it under
the identity `qwen3.8-27b-refusal-dial`

## Target identity and route predicates

Policy applies only after route resolution has made the public model group,
deployment provider, and resolved upstream model available. Matching is
case-sensitive

The NAS predicate is true only when all of these conditions hold:

1. The resolved LiteLLM model group is exactly
   `qwen3.8-27b-refusal-dial`
2. The selected deployment uses the hosted-vLLM transport
3. The resolved upstream model, after removing exactly one
   `hosted_vllm/` transport prefix when present, is exactly
   `qwen3.8-27b-refusal-dial`

The Fedora predicate is true only when all of these conditions hold:

1. The resolved LiteLLM model group is exactly
   `qwen3.8-27b-refusal-dial`
2. The selected deployment uses the LiteLLM-proxy transport to NAS
3. The resolved upstream model, after removing exactly one transport prefix
   used by that LiteLLM-proxy deployment when present, is exactly
   `qwen3.8-27b-refusal-dial`

The checkpoint name is deployment evidence, not an alternate public or route
identity. Substring, suffix, checkpoint-name, `base_model`, display-name,
family-only, alias-only, upstream-only, and one-deployment matches do not
satisfy either predicate. In particular, the policy must not match Qwen3.5,
Qwen3.6, or another Qwen alias

Each proxy validates its own resolved hop before making any network call.
Fedora does not rely on NAS as its only enforcement boundary, and NAS repeats
validation when it receives a Fedora request

## Public modes and defaults

The public enum is exactly this ordered set:

| Public mode | Terminal LiteLLM control sent to vLLM |
| --- | --- |
| `off` | omit `reasoning_effort`; set `chat_template_kwargs.enable_thinking=false` |
| `low` | `reasoning_effort=low` |
| `medium` | `reasoning_effort=medium` |
| `xhigh` | `reasoning_effort=xhigh` |

`low`, `medium`, and `xhigh` are exact native values. `off` is a semantic
public mode implemented through the Qwen template's native
`enable_thinking=false` switch. LiteLLM must not forward
`reasoning_effort=off` to vLLM

Omitting the reasoning field is allowed. Omission adds no reasoning control
and preserves the deployed template default, currently `xhigh`. Omission is
not a fifth selectable mode and clients must not display a default sentinel

Supplying null, an empty string, a differently cased value, `none`, `minimal`,
`high`, `max`, or any other value is unsupported. vLLM compatibility behavior
may map wire values such as `none` or `high`, but that generic compatibility
does not enlarge this model's public contract. Both proxies reject those
values before forwarding

## Final-payload normalization and conflicts

Validation runs on the final resolved request payload after configuration,
provider options, client options, and endpoint adaptation have merged. This
prevents a later merge from bypassing or overwriting the policy

The shared target policy accepts one semantic source value. Chat Completions
uses top-level `reasoning_effort`; Responses uses `reasoning.effort`. If an
endpoint bridge or compatibility layer produces more than one candidate, it
must first apply LiteLLM's existing conflict contract. Different supplied
values must fail; the Qwen policy must not choose one silently

`chat_template_kwargs.enable_thinking` is reserved output of this policy for
the target. A caller-supplied value is not a public reasoning surface and must
fail before forwarding, including when it happens to be `false`. This prevents
private template controls from bypassing the four-mode enum and makes
normalization provenance unambiguous

After validation, terminal normalization is atomic:

- `off` removes the semantic reasoning field from the provider payload and
  produces `chat_template_kwargs.enable_thinking=false`, preserving unrelated
  existing template kwargs
- `low`, `medium`, and `xhigh` produce only their exact
  `reasoning_effort` value and do not add `enable_thinking`
- omission produces neither control

Fedora is a nonterminal enforcing hop. After validating an accepted public
value, it forwards that same semantic value to NAS instead of emitting a vLLM
template control. NAS validates the public value again and performs terminal
normalization. A request sent directly to NAS is validated and normalized by
NAS in the same way. Thus `off` remains public `off` between proxies and only
the LiteLLM instance making the vLLM call emits `enable_thinking=false`

If the final provider payload would contain both `enable_thinking=false` and a
native `reasoning_effort`, or if a later transform changes the normalized
control, the request fails before network forwarding. Implementations must not
silently drop, clamp, retry, or reconcile conflicting controls

## Rejection contract

Unsupported values and conflicts on the target fail deterministically through
LiteLLM's existing invalid-request contract. The error identifies the invalid
field or conflict and target model group, and lists the allowed public values
`off`, `low`, `medium`, and `xhigh`

The same policy applies to streaming and non-streaming requests. Every
rejected request makes zero upstream attempts. Chat Completions and Responses
must use one shared policy rather than divergent endpoint-specific enums

When the applicable deployment predicate is false, the guard is a no-op.
Existing DeepSeek translations, defaults, errors, and client representations,
including the reconciled DeepSeek `off` contract, remain unchanged

## Surface representations

### Chat Completions

Direct callers send a public value as top-level `reasoning_effort`:

```json
{
  "model": "qwen3.8-27b-refusal-dial",
  "reasoning_effort": "off"
}
```

LiteLLM accepts public `off`. NAS emits
`chat_template_kwargs.enable_thinking=false` when calling CachyOS. Fedora
validates and forwards public `off` to NAS, where NAS validates it again and
emits the same terminal template control. Neither proxy accepts a caller's
private template control

### Responses

Direct callers send the public value in the OpenAI-compatible reasoning
object:

```json
{
  "model": "qwen3.8-27b-refusal-dial",
  "reasoning": {
    "effort": "off"
  }
}
```

LiteLLM extracts `reasoning.effort` into the shared policy before the
completion bridge or provider transform. Its canonical upstream output is the
same as Chat Completions. A bridge must not convert public `off` to `none`

### `opencode-litellm`

For the exact public model identity, generated legacy metadata declares
reasoning support and exactly these ordered visible variants:

```json
{
  "off": { "reasoningEffort": "off" },
  "low": { "reasoningEffort": "low" },
  "medium": { "reasoningEffort": "medium" },
  "xhigh": { "reasoningEffort": "xhigh" }
}
```

The V2 model declares `capabilities.reasoning: true` and exactly this ordered
variant list:

```json
[
  { "id": "off", "body": { "reasoning_effort": "off" } },
  { "id": "low", "body": { "reasoning_effort": "low" } },
  { "id": "medium", "body": { "reasoning_effort": "medium" } },
  { "id": "xhigh", "body": { "reasoning_effort": "xhigh" } }
]
```

The preferred and required current adapter representation keeps the visible
ID and request value identical. In particular, `off` reaches LiteLLM as
public `off`; LiteLLM alone emits `enable_thinking=false`

No `none` or `high` private client alias is authorized by this contract. If a
verified OpenCode or Codex version cannot parse, retain, or transmit a public
value unchanged, that client slice stops before activation. A future private
wire alias would require an approved SCR amendment, a trusted adapter boundary
that cannot be reached by public callers, and tests proving both proxies still
reject public `none` and `high`. Such an alias would remain an implementation
detail and could never appear as a fifth mode

### OpenCode

OpenCode consumes variants generated by `opencode-litellm`. Local
`opencode.json` must not contain a manual Qwen3.8 variant list. It displays
exactly Off, Low, Medium, and XHigh in that order, with no default sentinel,
and sends the selected public value unchanged

OpenCode activation has a mandatory stop condition: the installed version
must parse, display, select, persist, and transmit all four values unchanged.
Any rewrite to `none`, `high`, or another value blocks activation and returns
the slice to PMA

### Codex

The configured Qwen3.8 catalog entry has `supported_reasoning_levels`
containing exactly `off`, `low`, `medium`, and `xhigh`. Its
`default_reasoning_level`, and active `model_reasoning_effort` when present,
must be one of those four values. With `wire_api = "responses"`, Codex sends
the selected public value unchanged as `reasoning.effort`

Codex has the same compatibility stop condition as OpenCode. Do not substitute
`none` for `off` or `high` for `xhigh`, and do not activate a partial catalog

## Verification gates

Implementation is complete only when all applicable gates pass:

1. Unit or contract tests prove both exact route predicates, all four accepted
   mappings, omission behavior, and no match for aliases, upstreams, Qwen
   near-matches, DeepSeek, and unrelated models
2. Tests reject null, empty, case variants, `none`, `minimal`, `high`, `max`,
   arbitrary unknown values, caller-supplied `enable_thinking`, and conflicting
   final controls with zero upstream calls
3. Chat Completions and Responses cover streaming and non-streaming requests,
   final-payload merging, conflict handling, and equal canonical output
4. Controlled CachyOS probes reconfirm native `enable_thinking=false`, `low`,
   `medium`, and `xhigh`, the omission default, and rejection or incompatibility
   of unsupported values before either proxy changes
5. NAS and Fedora request captures prove each proxy enforces its own boundary,
   Fedora-to-NAS `off` remains public `off`, terminal NAS emits the template
   control, and public callers cannot inject that private control
6. Plugin snapshots prove the exact legacy object and V2 ordered list, plus no
   change to DeepSeek or generic reasoning mappings
7. OpenCode and Codex compatibility gates pass before config activation, then
   catalog inspection and redacted captures prove each mode reaches LiteLLM
   unchanged
8. Live positive and negative probes pass through both public proxies, with
   health checks before and after each rollout boundary

Evidence records versions, redacted requests, statuses and error bodies,
upstream-attempt counts, normalized controls, test commands, and rollback
decisions. Results map to each implementation task's numbered acceptance
criteria

## Rollout and rollback

Roll out in dependency order: shared LiteLLM policy and endpoint integration,
NAS, Fedora, plugin, OpenCode, then Codex. Do not expose generated client modes
until both proxies enforce the public contract. Validate each boundary before
advancing

Each slice preserves a dated secret-free backup or versioned prior artifact
and documents exact reversal. Rollback is boundary-local:

- LiteLLM: restore the prior code or image and restart only the affected
  deployment
- Plugin: restore the prior published or installed plugin version
- OpenCode: restore the prior plugin lock/config and remove target-specific
  overrides
- Codex: restore the prior catalog and config together

Any unsupported value forwarded, route mismatch, mode rewrite, conflict
bypass, DeepSeek or unrelated-model regression, failed health check, or failed
client stop condition halts rollout. Roll back the current boundary before
proceeding

## Privacy and observability

Logs and evidence may include the model group, normalized mode or control,
endpoint, status, deployment identifier, and correlation identifier. They must
not include API keys, authorization headers, cookies, prompts, completion
text, tool arguments, full request bodies, or unredacted configuration and
environment dumps

Invalid caller values use a bounded or safely escaped representation so they
cannot inject logs or create unbounded records. Normal mode selection requires
no prompt or response-content logging

## Documentation obligations

Implementation tasks must link this contract and the approved SCR. Any change
to route identity, public enum, omission behavior, normalization, rejection or
conflict semantics, inter-proxy representation, client representation,
or compatibility stop condition requires an approved SCR update before
implementation

Deployment runbooks identify the public alias, both-hop route, CachyOS served
identity, and actual `unsloth/Qwen3.8-27B-NVFP4` checkpoint without treating
the checkpoint as a request identity
## 2026-08-26 Client-Owned Scope Override

The approved SCR now supersedes this document's proxy-enforcement requirements. LiteLLM remains a generic pass-through and does not reject model-specific Qwen3.8 effort values. OpenCode and Codex own the selectable set `off`, `low`, `medium`, `xhigh` and correct request serialization. Sections describing mandatory NAS/Fedora rejection are retained only as historical design context and must not be implemented or deployed.
