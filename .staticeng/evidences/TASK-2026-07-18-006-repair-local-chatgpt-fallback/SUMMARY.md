# NAS ChatGPT Public Fallback Repair

## Summary

Updated the eight DB-backed unqualified public GPT fallback rules through LiteLLM's supported `POST /fallback` admin API. Every applicable chain now contains account2, account3, and default exactly once in that order

No qualified profile pin, credential, retry/cooldown setting, Redis state, deployment, source file, or unrelated fallback was changed

## Applicable Groups

- `gpt-5.3-codex`
- `gpt-5.3-codex-spark`
- `gpt-5.4`
- `gpt-5.4-mini`
- `gpt-5.5`
- `gpt-5.6-luna`
- `gpt-5.6-sol`
- `gpt-5.6-terra`

Each group now falls back to `chatgpt-account2/<group>`, `chatgpt-account3/<group>`, then `chatgpt/<group>`

## Backup

The pre-change sanitized routing snapshot is `.staticeng/evidences/TASK-2026-07-18-006-repair-local-chatgpt-fallback/logs/routing-before-sanitized.log`. It contains model-group names, fallback order, policy values, and deployment counts only. It contains no credential, token, prompt, response, user, or authentication content

## Validation

- `GET /router/settings` returned all eight exact chains with one rule per public source group
- `GET /fallback/{model}` returned HTTP 200 and the exact chain for all eight groups
- `GET /model/info` confirmed one public, account2, account3, and default Responses deployment for each applicable group; all remain DB-backed
- The fallback rule count remained 16, qualified rules were unchanged, and all eight non-public rules retained their original contents and order
- Retry/cooldown policy remained `num_retries=1`, `max_fallbacks=5`, `allowed_fails=1`, `cooldown_time=30`, `retry_after=0`, and `retry_policy=null`
- Readiness returned HTTP 200; the container remained healthy with zero restarts

## Bounded Responses Validation

Exactly one stateless request was sent to `/v1/responses` for public group `gpt-5.6-luna`, selected from current pre-request rate-limit evidence. The request set `store=false` and `max_retries=0`; no manual retry or second request was made

The bounded router window showed account2, account3, and default groups being attempted, proving advancement through the corrected chain. The request ended with HTTP 400 because the provider rejected the minimal input. No 429 occurred during this probe, so AC-5's narrower rate-limit-triggered advancement claim is not proven by the new request. The one-request ceiling prevents a corrective probe

No prompt, response, user, authorization, token, or raw log content was retained

## Acceptance Criteria

- AC-1: PASS; all eight applicable public groups have account2, account3, and default exactly once in order
- AC-2: PASS; qualified `chatgpt/*` fallback rules remained byte-for-byte equivalent at the sanitized structural level and no account2/account3 fallback was added to them
- AC-3: PASS; deployments, credentials, retry/cooldown policy, Redis, and unrelated routing were not changed
- AC-4: PASS; supported API readback plus `GET /fallback/{model}` non-inference validation proved the corrected chains
- AC-5: PARTIAL; one bounded no-retry stateless Responses request proved account-group advancement, but did not reproduce a 429 in its window
- AC-6: PASS; this summary and sanitized logs trace the implementation and validation; documentation impact is closed

## Evidence Files

- `.staticeng/evidences/TASK-2026-07-18-006-repair-local-chatgpt-fallback/logs/routing-before-sanitized.log`
- `.staticeng/evidences/TASK-2026-07-18-006-repair-local-chatgpt-fallback/logs/admin-update-sanitized.log`
- `.staticeng/evidences/TASK-2026-07-18-006-repair-local-chatgpt-fallback/logs/readback-validation-sanitized.log`
- `.staticeng/evidences/TASK-2026-07-18-006-repair-local-chatgpt-fallback/logs/bounded-responses-validation-sanitized.log`

## Documentation Impact

No product documentation change is required. This was a DB-backed operational routing repair and the evidence packet is the durable task record

## Residual Risk

The live probe proves configured fallback traversal but not specifically traversal caused by a newly observed rate-limit response. Do not send another request under this task because the allowed one-request ceiling has been consumed

## Reopen 1 Resolution

No fallback update was repeated. Exactly one corrective stateless `store=false`, `max_retries=0` request used the string-input Codex request shape covered by `tests/test_litellm/llms/chatgpt/responses/test_chatgpt_responses_transformation.py`. The public group was `gpt-5.3-codex`, which had current pre-request rate-limit evidence among the public ChatGPT groups

The sanitized router window proved traversal through account2, account3, and default. The final deployment header correlated to the default account deployment. No 429 occurred during this request; the provider returned HTTP 400 on every traversed account because `gpt-5.3-codex` is not supported by the current ChatGPT account-backed Codex provider

This is the exact remaining provider blocker permitted by the reopen contract. The corrective one-request allowance is consumed, so no further request was sent. AC-5 remains partial: routing advancement is proven, but rate-limit-triggered advancement to a successful account or a valid HTTP 200 cannot be demonstrated while this selected Codex model is rejected by the provider

Sanitized corrective evidence is `.staticeng/evidences/TASK-2026-07-18-006-repair-local-chatgpt-fallback/logs/reopen1-corrective-responses-sanitized.log`. No prompt, response, user, authentication, token, or raw log content was retained
