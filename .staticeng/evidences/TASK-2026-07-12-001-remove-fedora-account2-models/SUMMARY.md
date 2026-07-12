# Fedora Account2 Model Removal Evidence

## Summary

Removed all 7 Fedora LiteLLM deployments whose public name started with `chatgpt-account2/` and the corresponding 7 entries from the Fedora OpenCode LiteLLM plugin override catalog. Both post-removal inventories contain zero matching entries and preserve every non-target entry exactly.

## Work Performed

- Captured a sanitized `GET /model/info` inventory containing only deployment names and IDs
- Selected targets strictly by the `chatgpt-account2/` model-name prefix
- Deleted each target through `POST /model/delete` using its exact deployment ID
- Captured and compared the post-removal inventory
- Checked model endpoints, readiness, liveliness, and Docker health without invoking any model
- Backed up `/home/staticduo/.config/opencode/opencode.json` with mode `0600`
- Structurally removed account2 keys only from `plugin[4]` (`@staticeng/opencode-litellm`) `options.overrides`
- Compared sanitized non-target and non-catalog digests, then validated JSON and resolved OpenCode config loading

## Acceptance Criteria Coverage

- AC-1: PASS; account2 count changed from 7 to 0
- AC-2: PASS; all 7 regular `chatgpt/*` name and ID pairs are unchanged
- AC-3: PASS; all 12 non-account2 name and ID pairs are unchanged
- AC-4: PASS; `/model/info`, `/v1/models`, `/health/readiness`, and `/health/liveliness` returned HTTP 200; the `litellm` container is running and healthy
- AC-5: PASS; no auth flow, inference request, credential file inspection, or auth file access/change was performed
- AC-6: PASS; this packet contains the sanitized before inventory, deletion results, and verification log
- AC-7: PASS; the OpenCode plugin override has zero account2 entries, while non-target override and all other config digests match before and after

## Removed Models

- `chatgpt-account2/gpt-5.3-codex`
- `chatgpt-account2/gpt-5.4`
- `chatgpt-account2/gpt-5.4-mini`
- `chatgpt-account2/gpt-5.5`
- `chatgpt-account2/gpt-5.6-luna`
- `chatgpt-account2/gpt-5.6-sol`
- `chatgpt-account2/gpt-5.6-terra`

## Documentation Impact

No product documentation changes are required. Added sanitized OpenCode configuration evidence and rollback commands to this task packet.

## Open Risks

The first API deletion's HTTP status was not captured because a shell-reserved variable caused an error after the request completed; a repeated request returned HTTP 400 and the post-inventory proves that exact deployment was removed. No process restart was performed; existing OpenCode sessions retain their startup-time config until their owner restarts them, while new processes load the validated updated config.

## Recommended Next Step

Have the task reviewer validate this evidence packet and close the task.
