# TASK-2026-08-25-003 Evidence Summary

## Result

Implemented the target-specific DeepSeek V4 hosted-vLLM reasoning policy for Chat Completions, native Responses, and the Responses-to-Chat bridge. Reopen 1 moved enforcement after `extra_body`; Reopen 2 added native Responses compatibility-field resolution and explicit dual-representation conflicts. No deployment or client configuration was changed

## Acceptance Criteria

- AC-1: PASS. Focused tests accept omitted effort and exact public values `off`, `low`, `high`, and `max`
- AC-2: PASS. Payload assertions prove `off` and `thinking.type=disabled` become `none`; native values pass unchanged
- AC-3: PASS. Negative tests cover unsupported values, post-transform injection, top-level Responses compatibility values, and conflicting nested/top-level representations with deterministic status 400 errors
- AC-4: PASS. Native Responses and streaming/non-streaming Responses bridge tests use the shared target policy
- AC-5: PASS. Exact two-part identity tests prove near matches and unrelated hosted-vLLM models retain existing behavior; non-reasoning parameters remain intact
- AC-6: PASS. Focused suite completed with 59 passing tests. Transport tests prove zero HTTP posts for sync, async, stream/non-stream compatibility-only invalid values and mixed-representation conflicts
- AC-7: PASS. Added the hosted-vLLM module CodeMap, updated navigable module maps, this task record, and complete logs

## Verification Logs

- `.staticeng/evidences/TASK-2026-08-25-003-implement-deepseek-hosted-vllm-policy/logs/focused-tests.log`: 59 passed
- `.staticeng/evidences/TASK-2026-08-25-003-implement-deepseek-hosted-vllm-policy/logs/ruff.log`: all checks passed
- `.staticeng/evidences/TASK-2026-08-25-003-implement-deepseek-hosted-vllm-policy/logs/type-check.log`: shared policy module has zero errors and warnings; surrounding legacy transformation modules retain pre-existing strict typing debt
- `.staticeng/evidences/TASK-2026-08-25-003-implement-deepseek-hosted-vllm-policy/logs/diff-check.log`: clean
- `.staticeng/evidences/TASK-2026-08-25-003-implement-deepseek-hosted-vllm-policy/logs/staticeng-validate.log`: repository-wide validation remains blocked by pre-existing missing CodeMaps outside this task scope; dry-run repair confirms they require module-boundary decisions

## Documentation Impact

The approved architecture contract and SCR already describe the resulting behavior, so no steady-state product or architecture text required changes. CodeMaps were updated for the new shared policy source

## Reopen 1

The final merged outbound payload is now authoritative. Generic Chat and Responses provider configs expose a no-op `finalize_request` hook; hosted-vLLM overrides it to validate and normalize only the exact DeepSeek target after all supported `extra_body` merges. This preserves existing precedence, where `extra_body` overrides the transformed payload, while ensuring the overriding value must satisfy the approved model contract

## Reopen 2

Native Responses now treats nested `reasoning.effort` and top-level compatibility `reasoning_effort` as equivalent caller representations. A single representation is validated and canonicalized into nested `reasoning.effort`; equal dual values are accepted and canonicalized; unequal dual values are rejected explicitly before transport. Unrelated hosted-vLLM models retain both fields unchanged
