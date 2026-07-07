# TASK-2026-07-07-011 Evidence Summary

Root cause: ChatGPT's Responses stream returns `response.completed` with `response.output: []`, while the actual assistant message is present earlier in `response.output_item.done` and `response.output_text.done`. The direct ChatGPT non-stream response parser already recovered this, but the Chat Completions bridge consumes the Responses streaming iterator and then transforms `completed_response.response.output`. That iterator was not carrying forward streamed output items into the completed response, so the bridge saw `[]` and raised `Unknown items in responses API response: []`.

Fix: `litellm/responses/streaming_iterator.py` now records recovered output from the transformed streaming event after provider and stream post-processing, then attaches the recovered output items to `response.completed.response.output` only when the completed response output is empty. This preserves non-empty completed outputs and keeps output recovery consistent with emitted streaming events.

Reopen resolution: additional regression tests cover `output_text.done`-only recovery, `output_item.done` precedence over `output_text.done`, non-empty completed output preservation, provider transform normalization, and post-processing normalization via encrypted-content wrapping. The local LiteLLM container was hot-patched with the reopened change and restarted for live validation only; no Fedora deployment was performed.

Safe evidence logs:
- `logs/safe-live-diagnostics.jsonl`: sanitized profile/header/request/upstream event-shape comparison
- `logs/unit-tests.txt`: focused test command output
- `logs/live-smoke-after-hotpatch.jsonl`: sanitized proxy smoke results after local hot-patch
- `logs/local-container-hotpatch.txt`: local validation deployment note
- `logs/reopen-resolution.txt`: critic finding resolution and rerun commands

No access tokens, refresh tokens, cookies, API keys, master keys, DB URLs, auth files, raw auth headers, or raw ChatGPT bodies are included.
