---
id: TASK-2026-05-29-003
title: Fix ChatGPT Responses streaming usage parse failure
status: active
complexity: standard
track: implementation
slice: logic
assigned_to: developer
handoff_from: product_manager
created_at: 2026-05-29
scr: none
parent: TASK-2026-05-29-002
---

# Task: Fix ChatGPT Responses Streaming Usage Parse Failure

## Classification

- Complexity: `standard`
- Track: `implementation`
- Slice: `logic`

## Production Problem

Live LiteLLM is healthy at container/DB level but `chatgpt/gpt-5.5` streaming calls can fail with:

```text
RateLimitError: ChatgptException - Error parsing chunk: 2 validation errors for ResponseAPIUsage
input_tokens Field required
output_tokens Field required
```

The logged raw chunk shows a Responses streaming event whose `response.usage` is in chat-completions style:

```json
{
  "completion_tokens": 267,
  "prompt_tokens": 29732,
  "total_tokens": 29999,
  "completion_tokens_details": {...},
  "prompt_tokens_details": {...}
}
```

but the Responses API pydantic event expects `ResponseAPIUsage` with `input_tokens` and `output_tokens`.

This also causes very large raw prompt dumps in Docker logs because the stream parse exception includes the received chunk/request context.

## Acceptance Criteria

- AC-1: Normalize Responses streaming `response.usage` before pydantic validation when it arrives in chat usage format (`prompt_tokens`/`completion_tokens`).
- AC-2: Preserve standard Responses usage format (`input_tokens`/`output_tokens`) unchanged.
- AC-3: Preserve usage detail fields as much as possible while mapping prompt->input and completion->output details.
- AC-4: Add focused regression tests for `response.completed` chunks with chat-style usage.
- AC-5: Run focused tests and formatting checks.
- AC-6: Deploy a fixed Docker image or, if forward fix blocks, rollback to the last known working image and report clearly.
- AC-7: Verify LiteLLM health and scan recent logs for absence of `ResponseAPIUsage` parse errors and raw prompt dumps after deploy/rollback.

## Constraints

- Do not expose secrets, raw prompts, cookies, tokens, DB URLs, or full request payloads in final output/evidence.
- Do not touch upstream PR worktree `/tmp/opencode/litellm-lazymcp-reopen-20260519`.
- Keep the fix minimal and targeted to Responses streaming usage parsing.
- If release script is used, keep rollback image behavior.

## Expected Evidence

Create `evidences/TASK-2026-05-29-003-fix-chatgpt-response-usage-parse/` with:

- `SUMMARY.md` mapping AC-1..AC-7.
- `logs/focused-tests.log`.
- `logs/deploy-or-rollback.log`.
- `logs/health-after.log`.
- `logs/error-scan-after.log`.

## Handoff

[Agent Message] From: product_manager To: developer

Please fix live LiteLLM so ChatGPT Responses streaming events whose `response.usage` uses chat usage keys do not fail pydantic validation. Implement minimal normalization, test it, and deploy fixed image or rollback if forward fix blocks.
