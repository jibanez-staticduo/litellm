# Sanitized Live Routing Readback

- Captured at: `2026-08-19T08:06:14Z` through `2026-08-19T08:07:20Z`
- Fedora service: `litellm`, healthy
- Runtime mutation: none
- Secrets, identities, account IDs, and raw deployment IDs retained: none
- Deployment IDs below are one-way SHA-256 prefixes used only to distinguish records

| Public group | Provider model | Profile class | ID hash |
|---|---|---|---|
| `gpt-5.4` | `chatgpt/gpt-5.4` | non-default | `113209eed769` |
| `gpt-5.4-mini` | `chatgpt/gpt-5.4-mini` | non-default | `f8ca715d8a64` |
| `gpt-5.5` | `chatgpt/gpt-5.5` | non-default | `344514716469` |
| `gpt-5.6-luna` | `chatgpt/gpt-5.6-luna` | non-default | `3288ca4f32ca` |
| `gpt-5.6-sol` | `chatgpt/gpt-5.6-sol` | default | `b13140ba17c3` |
| `gpt-5.6-terra` | `chatgpt/gpt-5.6-terra` | non-default | `140266d30396` |

Each of the six public aliases also has one `chatgpt/<alias>` default deployment and one `chatgpt-account2/<alias>` non-default deployment. The related qualified deployment ID hashes are retained in sanitized command output only as follows: default `854050d5a509`, `f09c8eac1e9a`, `5c34721a9788`, `32cd9d4142ad`, `9f976ead00cb`, `89afa79480bc`; account2 `de737b49fc3e`, `8cfae06d95ba`, `b57c7a808a4d`, `0acd4d6d9b1d`, `a015937e9f4b`, `2a87a0004f29`

General public fallback rules:

| Public alias | Live fallback target |
|---|---|
| `gpt-5.4` | `chatgpt/gpt-5.4` |
| `gpt-5.4-mini` | `chatgpt/gpt-5.4-mini` |
| `gpt-5.5` | `chatgpt/gpt-5.5` |
| `gpt-5.6-luna` | missing |
| `gpt-5.6-sol` | `chatgpt-account2/gpt-5.6-sol` |
| `gpt-5.6-terra` | `chatgpt/gpt-5.6-terra` |

Every inspected qualified account1 group has a matching account2 fallback, including `chatgpt/gpt-5.6-sol -> chatgpt-account2/gpt-5.6-sol`. Router settings were `allow_chatgpt_cross_profile_fallback=true`, `allowed_fails=1`, `cooldown_time=30.0`, `num_retries=3`, and `routing_strategy=simple-shuffle`. No context-window or content-policy fallback was configured
