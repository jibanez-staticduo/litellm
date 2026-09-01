# TASK-2026-08-25-016 Evidence

## Result

Activated the reviewed local `opencode-litellm` 0.1.9 artifact in the owner-only global OpenCode configuration by changing only the installed plugin reference. OpenCode 1.18.21 resolves the contract-owned variants for both aliases, and isolated loopback inference captured every selected public effort without contacting production during the successful verification

## Acceptance Criteria Coverage

- AC-1: PASS. `.staticeng/evidences/TASK-2026-08-25-016-activate-local-opencode-deepseek-variants/logs/baseline-and-rollback.log` records the owner-only backup, baseline and active checksums, permissions, prior and active plugin references, artifact checksum, and exact rollback command
- AC-2: PASS. The active tuple now references `file:///home/staticduo/git/opencode-litellm/dist/index.js`; no manual DeepSeek model or variant override was added
- AC-3: PASS. `.staticeng/evidences/TASK-2026-08-25-016-activate-local-opencode-deepseek-variants/logs/resolved-variants.log` records exact `off`, `low`, `high`, and `max` resolution for both aliases on legacy and V2 config surfaces, with `medium` and `xhigh` absent
- AC-4: PASS. `.staticeng/evidences/TASK-2026-08-25-016-activate-local-opencode-deepseek-variants/logs/sanitized-loopback-bodies.jsonl` contains eight redacted OpenCode request captures, one per alias and mode. Each body reaches `127.0.0.1` with the selected public effort unchanged
- AC-5: PASS. `.staticeng/evidences/TASK-2026-08-25-016-activate-local-opencode-deepseek-variants/logs/semantic-config-comparison.log` proves semantic equality after normalizing the one approved reference change, zero manual target overrides before and after, and preserved mode `0600`
- AC-6: PASS. This packet documents rollback and the later repin: replace only `file:///home/staticduo/git/opencode-litellm/dist/index.js` with `@staticeng/opencode-litellm@0.1.9` after immutable publication and rereun the same gates

## Safety Note

An initial isolation attempt incorrectly used `OPENCODE_CONFIG_CONTENT` over the active global config, so the global tuple options retained the production base URL and one `off` request was rejected by production before inference. No prompt reached a model and no completion was generated. Verification stopped immediately, then reran with an isolated `XDG_CONFIG_HOME`; all retained successful request-body evidence is loopback-only and sanitized

## Documentation Impact

No product or architecture documentation change is required. The approved SCR and steady-state reasoning contract already specify the local OpenCode behavior. This evidence adds only deployment and rollback records

## Validation

`git diff --check` passes for the task-owned artifacts. `staticeng_validate` still fails on the repository's pre-existing broad missing-CodeMap backlog; `staticeng_repair` dry-run confirms the unresolved items require module-boundary decisions and are unrelated to this configuration-only task

## Rollback

Restore the owner-only backup exactly as recorded in `.staticeng/evidences/TASK-2026-08-25-016-activate-local-opencode-deepseek-variants/logs/baseline-and-rollback.log`. The backup remains outside the repository beside the active config
