# Sanitized Probe And Log Results

- Probe window: `2026-08-19T08:07:20Z` through `2026-08-19T08:07:29Z`
- Requests sent: exactly 3
- Client retries: 0
- Request shape: list-form user `input_text`, `reasoning.context=all_turns`, effort `high`, summary `detailed`, `stream=true`, `store=false`, encrypted-reasoning inclusion, parallel tool calls disabled, Codex Responses Lite header
- Request and response content retained: none

| Probe | HTTP | Terminal selected group | Completions | Sanitized error class |
|---|---:|---|---:|---|
| Qualified account1 `chatgpt/gpt-5.6-sol` | 200 | `chatgpt-account2/gpt-5.6-sol` | 1 | none |
| Qualified account2 `chatgpt-account2/gpt-5.6-sol` | 200 | `chatgpt-account2/gpt-5.6-sol` | 1 | none |
| Unqualified `gpt-5.6-sol` | 200 | `chatgpt-account2/gpt-5.6-sol` | 1 | none |

The terminal account2 selection for qualified account1 and public Sol is fresh contradictory behavior: both routes advanced and completed instead of returning the account1 quota error. The direct account2 completion excludes authentication failure, request-shape failure, unsupported model, and deployment outage

The bounded container-log window `2026-08-19T08:07:15Z` through `2026-08-19T08:07:35Z` contained five infrastructure lines and zero sanitized matches for quota/rate-limit, fallback error, authentication error, or invalid request shape. No content-bearing log line was retained
