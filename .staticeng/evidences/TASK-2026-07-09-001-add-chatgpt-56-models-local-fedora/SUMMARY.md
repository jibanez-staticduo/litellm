# Evidence Summary: TASK-2026-07-09-001-add-chatgpt-56-models-local-fedora

## Summary
Registered the requested ChatGPT 5.6 aliases on local/NAS LiteLLM and Fedora LiteLLM using the LiteLLM admin API (`POST /model/new`). No application code, images, deployments, auth files, or account2 authentication flows were changed.

## Local/NAS Models
| Model | Status | Provider model | Profile | Template |
|---|---:|---|---|---|
| `chatgpt/gpt-5.6-sol` | created | `chatgpt/gpt-5.6-sol` | default | `chatgpt/gpt-5.5` |
| `chatgpt/gpt-5.6-terra` | created | `chatgpt/gpt-5.6-terra` | default | `chatgpt/gpt-5.5` |
| `chatgpt/gpt-5.6-luna` | created | `chatgpt/gpt-5.6-luna` | default | `chatgpt/gpt-5.5` |
| `chatgpt-account2/gpt-5.6-sol` | created | `chatgpt/gpt-5.6-sol` | account2 | `chatgpt-account2/gpt-5.5` |
| `chatgpt-account2/gpt-5.6-terra` | created | `chatgpt/gpt-5.6-terra` | account2 | `chatgpt-account2/gpt-5.5` |
| `chatgpt-account2/gpt-5.6-luna` | created | `chatgpt/gpt-5.6-luna` | account2 | `chatgpt-account2/gpt-5.5` |

## Fedora Models
| Model | Status | Provider model | Profile | Template |
|---|---:|---|---|---|
| `chatgpt/gpt-5.6-sol` | created | `chatgpt/gpt-5.6-sol` | default | `chatgpt/gpt-5.5` |
| `chatgpt/gpt-5.6-terra` | created | `chatgpt/gpt-5.6-terra` | default | `chatgpt/gpt-5.5` |
| `chatgpt/gpt-5.6-luna` | created | `chatgpt/gpt-5.6-luna` | default | `chatgpt/gpt-5.5` |
| `chatgpt-account2/gpt-5.3-codex` | created | `chatgpt/gpt-5.3-codex` | account2 | `chatgpt/gpt-5.3-codex` |
| `chatgpt-account2/gpt-5.4` | created | `chatgpt/gpt-5.4` | account2 | `chatgpt/gpt-5.4` |
| `chatgpt-account2/gpt-5.4-mini` | created | `chatgpt/gpt-5.4-mini` | account2 | `chatgpt/gpt-5.4-mini` |
| `chatgpt-account2/gpt-5.5` | created | `chatgpt/gpt-5.5` | account2 | `chatgpt/gpt-5.5` |
| `chatgpt-account2/gpt-5.6-luna` | created | `chatgpt/gpt-5.6-luna` | account2 | `chatgpt-account2/gpt-5.5` |
| `chatgpt-account2/gpt-5.6-sol` | created | `chatgpt/gpt-5.6-sol` | account2 | `chatgpt-account2/gpt-5.5` |
| `chatgpt-account2/gpt-5.6-terra` | created | `chatgpt/gpt-5.6-terra` | account2 | `chatgpt-account2/gpt-5.5` |

## Acceptance Criteria Coverage
| AC | Result | Evidence |
|---|---|---|
| AC-1 | Pass | Local default models `chatgpt/gpt-5.6-sol`, `chatgpt/gpt-5.6-terra`, `chatgpt/gpt-5.6-luna` were created from `chatgpt/gpt-5.5`; `.staticeng/evidences/TASK-2026-07-09-001-add-chatgpt-56-models-local-fedora/logs/settings_comparison.json` shows only `provider_model` differs. |
| AC-2 | Pass | Local account2 models `chatgpt-account2/gpt-5.6-sol`, `chatgpt-account2/gpt-5.6-terra`, `chatgpt-account2/gpt-5.6-luna` were created with `chatgpt_auth_profile: account2`; see `.staticeng/evidences/TASK-2026-07-09-001-add-chatgpt-56-models-local-fedora/logs/local_mutation.json`. |
| AC-3 | Pass | Fedora default models `chatgpt/gpt-5.6-sol`, `chatgpt/gpt-5.6-terra`, `chatgpt/gpt-5.6-luna` were created from Fedora `chatgpt/gpt-5.5`; see `.staticeng/evidences/TASK-2026-07-09-001-add-chatgpt-56-models-local-fedora/logs/settings_comparison.json`. |
| AC-4 | Pass | Fedora account2 models were created for `gpt-5.3-codex`, `gpt-5.4`, `gpt-5.4-mini`, `gpt-5.5`, and the three new `gpt-5.6-*` aliases; see `.staticeng/evidences/TASK-2026-07-09-001-add-chatgpt-56-models-local-fedora/logs/fedora_mutation.json`. |
| AC-5 | Pass | Inventory comparison shows no removed pre-existing ChatGPT models and `preserved_all_preexisting: true` for both instances; see `.staticeng/evidences/TASK-2026-07-09-001-add-chatgpt-56-models-local-fedora/logs/inventory_comparison.json`. |
| AC-6 | Pass | Local and Fedora `/health/readiness`, `/v1/models`, and `/model/info` returned HTTP 200 with required models present; see health/admin validation logs. |
| AC-7 | Pass | No completion calls or auth endpoints were used; only `/health/readiness`, `/v1/models`, `/model/info`, and `/model/new` admin registration calls were made. |
| AC-8 | Pass | Evidence packet contains this `SUMMARY.md` and secret-safe logs under `.staticeng/evidences/TASK-2026-07-09-001-add-chatgpt-56-models-local-fedora/logs/`. |

## Validation Highlights
- Local: `/health/readiness` HTTP 200; `/model/info` HTTP 200 with 16 ChatGPT models; `/v1/models` HTTP 200 with required models present.
- Fedora: `/health/readiness` HTTP 200; `/model/info` HTTP 200 with 14 ChatGPT models; `/v1/models` HTTP 200 with required models present.
- Inventory delta: local added 6 ChatGPT rows; Fedora added 10 ChatGPT rows; removed rows: local 0, Fedora 0.

## Logs
- `.staticeng/evidences/TASK-2026-07-09-001-add-chatgpt-56-models-local-fedora/logs/local_pre_inventory.json`
- `.staticeng/evidences/TASK-2026-07-09-001-add-chatgpt-56-models-local-fedora/logs/fedora_pre_inventory.json`
- `.staticeng/evidences/TASK-2026-07-09-001-add-chatgpt-56-models-local-fedora/logs/local_mutation.json`
- `.staticeng/evidences/TASK-2026-07-09-001-add-chatgpt-56-models-local-fedora/logs/fedora_mutation.json`
- `.staticeng/evidences/TASK-2026-07-09-001-add-chatgpt-56-models-local-fedora/logs/local_post_inventory.json`
- `.staticeng/evidences/TASK-2026-07-09-001-add-chatgpt-56-models-local-fedora/logs/fedora_post_inventory.json`
- `.staticeng/evidences/TASK-2026-07-09-001-add-chatgpt-56-models-local-fedora/logs/inventory_comparison.json`
- `.staticeng/evidences/TASK-2026-07-09-001-add-chatgpt-56-models-local-fedora/logs/settings_comparison.json`
- `.staticeng/evidences/TASK-2026-07-09-001-add-chatgpt-56-models-local-fedora/logs/local_health_admin_validation.json`
- `.staticeng/evidences/TASK-2026-07-09-001-add-chatgpt-56-models-local-fedora/logs/fedora_health_admin_validation.json`

## Open Risks
- Fedora account2 models are visible but intentionally unauthenticated until the user performs account2 authentication later.
- No live ChatGPT completion calls were run for account2, by request.

