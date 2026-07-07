---
id: DISCUSSION-004
title: "Debug and fix ChatGPT account2 empty Responses output"
status: closed
summarized_by: product_manager
source: runtime-transcript
---

# Discussion Summary

## Topic
The account2 ChatGPT models authenticated successfully but `chatgpt-account2/gpt-5.5` and `chatgpt-account2/gpt-5.4` failed with `Unknown items in responses API response: []`, while the default `chatgpt/gpt-5.5` path worked.

## Root Cause
ChatGPT can stream the actual assistant message in `response.output_item.done` and `response.output_text.done` events while the terminal `response.completed.response.output` is empty. LiteLLM's Chat Completions bridge consumed the Responses streaming iterator and transformed only the terminal completed response output, so it saw `[]` and raised the parser error.

## Fix
`litellm/responses/streaming_iterator.py` now records transformed/post-processed streamed output items and attaches them to the completed response only when completed output is empty. Non-empty completed output remains authoritative.

## Verification
- Focused tests passed: `37 passed`.
- Ruff check/format passed for touched files.
- Local hotpatch smokes passed for `chatgpt/gpt-5.5`, `chatgpt-account2/gpt-5.5`, and `chatgpt-account2/gpt-5.4`.
- Durable local/NAS image was built and deployed after commit `fe302bf88d`.
- Durable image smokes passed for the same three models using sanitized `/v1/responses` probes.

## Release Outcome
- Deployed image: `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-chatgptprofiles-emptyoutputfix-20260708`.
- Digest: `docker.staticduo.com/litellm@sha256:1c83fa329b7c3e5d4e04ccd03da9a345c373d24123b6a0b060de4d178f6c1316`.
- Rollback: `docker.staticduo.com/litellm:rollback-account2-emptyoutputfix-20260708`.

## Follow-Up
Monitor account2 ChatGPT traffic. No Fedora deployment was performed.
