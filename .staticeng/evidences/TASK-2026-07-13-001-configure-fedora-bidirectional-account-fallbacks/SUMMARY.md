# Fedora Bidirectional Account Fallback Evidence

## Summary

Configured database-backed bidirectional fallbacks for all seven matching Fedora `chatgpt/*` and `chatgpt-account2/*` model-group pairs. Enabled the trusted cross-profile policy in the same database-backed router settings record, restarted LiteLLM, and confirmed persistent and live state match.

## Exact Pairs

- `chatgpt/gpt-5.3-codex` <-> `chatgpt-account2/gpt-5.3-codex`
- `chatgpt/gpt-5.4` <-> `chatgpt-account2/gpt-5.4`
- `chatgpt/gpt-5.4-mini` <-> `chatgpt-account2/gpt-5.4-mini`
- `chatgpt/gpt-5.5` <-> `chatgpt-account2/gpt-5.5`
- `chatgpt/gpt-5.6-luna` <-> `chatgpt-account2/gpt-5.6-luna`
- `chatgpt/gpt-5.6-sol` <-> `chatgpt-account2/gpt-5.6-sol`
- `chatgpt/gpt-5.6-terra` <-> `chatgpt-account2/gpt-5.6-terra`

## Persistence And Loading

- General fallbacks were written through `POST /fallback` with `fallback_type: general`
- The endpoint persists the complete router settings object in PostgreSQL table `LiteLLM_Config`, row `param_name = 'router_settings'`
- `allow_chatgpt_cross_profile_fallback: true` was added directly to that JSON row because the deployed API exposes no router-settings write endpoint
- On startup, `ProxyConfig.get_config()` merges the DB `router_settings` record into config before constructing `Router`; `Router.get_valid_args()` accepts the policy constructor option
- Runtime DB synchronization also reads the row, but `Router.update_settings()` does not support this constructor-only policy; restart was therefore required and performed
- Request-level router overrides allow only fallback/retry fields and do not expose the cross-profile policy

## Preservation

All seven pre-existing fallback rules were retained in their original order. Pair fallbacks were inserted first for sources that already had fallbacks. In particular, the existing `deepseek-v4-flash-fp8-mtp` fallback remains second for `chatgpt/gpt-5.4` and `chatgpt/gpt-5.5`. Unrelated fallback rules and model groups were not changed.

## Validation

- Fedora LiteLLM returned healthy after restart
- `/model/info` returned seven matching pairs
- Persistent DB state contains 19 general fallback rules, including 14 pair source rules, and policy `true`
- Live `/router/settings` contains the same 19 rules and policy `true`
- Every pair source has its counterpart as the first fallback in both directions
- The live router settings field metadata does not list the policy, so it is not offered as a client-configurable request field

## QA Failover Validation

QA made exactly one minimal request to `chatgpt/gpt-5.6-sol`, with no manual retry. The regular primary returned HTTP 200 and matched its harmless sentinel, so the configured account2 fallback was not needed or exercised. The selected regular deployment is profile `default`, prefix `9007ab1c`, with initial attempt/reason `0 / initial selection`.

No account2 follow-up request was made because it was not needed; prior same-day evidence already proves account2 primary returned HTTP 200. No new device-code/auth prompt occurred.

No live reverse failure was forced because no natural account2 failure occurred. Reverse coverage uses the symmetric exact DB-backed/live rules and existing automated cross-profile/identity tests. PMA reran the focused routing/OAuth suite with the project `uv` environment: 49 tests passed with no skips; five Python 3.12 multiprocessing fork warnings were emitted.

## Secret Safety

No credentials, auth files, token values, YAML, or `.env` files were read or changed. Evidence contains only model-group names, safe router settings, endpoint names, counts, and health state.

## Evidence

- `inspection.log`
- `validation.log`
