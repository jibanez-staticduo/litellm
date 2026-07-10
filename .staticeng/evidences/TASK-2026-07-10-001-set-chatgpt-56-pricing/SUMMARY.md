# Evidence Summary: TASK-2026-07-10-001-set-chatgpt-56-pricing

## Summary
Updated LiteLLM pricing metadata for the six requested ChatGPT GPT-5.6 aliases on local/NAS and Fedora using the LiteLLM admin API (`POST /model/update`). No application code, images, deployments, auth endpoints, or completion calls were used.

## Pricing Source And Conversion
| Model tier | Source price per 1M input | Source price per 1M output | LiteLLM input_cost_per_token | LiteLLM output_cost_per_token |
|---|---:|---:|---:|---:|
| Sol | $5 | $30 | `0.000005` | `0.00003` |
| Terra | $2.50 | $15 | `0.0000025` | `0.000015` |
| Luna | $1 | $6 | `0.000001` | `0.000006` |

## Final Verified Values
| Instance | Alias | input_cost_per_token | output_cost_per_token | Verification |
|---|---|---:|---:|---|
| local | `chatgpt/gpt-5.6-sol` | `5e-06` | `3e-05` | PASS |
| local | `chatgpt/gpt-5.6-terra` | `2.5e-06` | `1.5e-05` | PASS |
| local | `chatgpt/gpt-5.6-luna` | `1e-06` | `6e-06` | PASS |
| local | `chatgpt-account2/gpt-5.6-sol` | `5e-06` | `3e-05` | PASS |
| local | `chatgpt-account2/gpt-5.6-terra` | `2.5e-06` | `1.5e-05` | PASS |
| local | `chatgpt-account2/gpt-5.6-luna` | `1e-06` | `6e-06` | PASS |
| fedora | `chatgpt/gpt-5.6-sol` | `5e-06` | `3e-05` | PASS |
| fedora | `chatgpt/gpt-5.6-terra` | `2.5e-06` | `1.5e-05` | PASS |
| fedora | `chatgpt/gpt-5.6-luna` | `1e-06` | `6e-06` | PASS |
| fedora | `chatgpt-account2/gpt-5.6-sol` | `5e-06` | `3e-05` | PASS |
| fedora | `chatgpt-account2/gpt-5.6-terra` | `2.5e-06` | `1.5e-05` | PASS |
| fedora | `chatgpt-account2/gpt-5.6-luna` | `1e-06` | `6e-06` | PASS |

## Update Scope
Only these pricing fields were updated through `/model/update`: `litellm_params.input_cost_per_token` and `litellm_params.output_cost_per_token`. Post-update `/model/info` confirms the equivalent `model_info.input_cost_per_token` and `model_info.output_cost_per_token` values now match on all target rows.

## Health/Admin Verification
- local: `/model/info` HTTP 200; `/health/readiness` HTTP 200; `/health/liveliness` HTTP 200
- fedora: `/model/info` HTTP 200; `/health/readiness` HTTP 200; `/health/liveliness` HTTP 200

## Preservation Check
- local: non-pricing sanitized `/model/info` fields preserved for all target aliases excluding the two cost fields: PASS
- fedora: non-pricing sanitized `/model/info` fields preserved for all target aliases excluding the two cost fields: PASS

## Logs
- `.staticeng/evidences/TASK-2026-07-10-001-set-chatgpt-56-pricing/logs/local_update_verify.json`
- `.staticeng/evidences/TASK-2026-07-10-001-set-chatgpt-56-pricing/logs/fedora_update_verify.json`
- `.staticeng/evidences/TASK-2026-07-10-001-set-chatgpt-56-pricing/logs/combined_verification.json`

## Open Risks
- No completion or ChatGPT auth calls were run by request, so this validates admin metadata and health only.
