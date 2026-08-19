# Routing And Functional Checks

## Persistent And Live Inventory

- Total model rows: 32
- Public GPT aliases: 8
- Public aliases bound to the default profile: 8 of 8
- Default-qualified deployments: 8
- Account2-qualified deployments: 8
- Account3 deployments: 0
- General fallback rules: 16
- Account3 fallback references across all general rules: 0
- Routing strategy: `simple-shuffle`
- Cross-profile fallback policy: enabled

All eight public fallback rules retain both default and account2 targets. Every unrelated fallback rule remains present, and the total rule count remains 16

## Bounded Production Checks

The final checks used the proven Codex Responses Lite request shape with list input, `reasoning.context=all_turns`, native streaming, no client retries, and a 180-second bound

- `chatgpt/gpt-5.6-sol`: HTTP 200, exactly one `response.completed`, no auth/device error
- `chatgpt-account2/gpt-5.6-sol`: HTTP 200, exactly one `response.completed`, no auth/device error
- `gpt-5.6-sol`: HTTP 200, exactly one `response.completed`, no auth/device error

An initial default-only probe omitted the required Codex Responses Lite header/request shape and returned HTTP 400 without an auth/device error. It was corrected before the three final gates above; no account3 request was made

Result: **PASS**
