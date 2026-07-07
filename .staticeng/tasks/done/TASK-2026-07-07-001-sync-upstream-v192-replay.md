---
task_id: TASK-2026-07-07-001-sync-upstream-v192-replay
complexity: complex
track: implementation
slice: core
status: done
assigned_to: workflow_runner
handoff_from: product_manager
scr: none
parent: none
discussion: DISCUSSION-003
---

# Sync StaticDuo LiteLLM Fork Onto Upstream v1.92

## Classification

- complexity: complex
- track: implementation
- slice: core

## Active Discussions

- DISCUSSION-003: Sync LiteLLM fork onto upstream v1.92 replay

## Context

The user wants the fork's main line to keep upstream BerriAI commits intact and replay StaticDuo's local commits on top, so future upstream updates remain easier.

Repository state at task creation:
- Worktree: `/home/staticduo/git/litellm`
- Current branch: `sync-upstream-v1.92`
- Remote `origin`: user's fork `git@github.com:jibanez-staticduo/litellm.git`
- Remote `upstream`: BerriAI `https://github.com/BerriAI/litellm`
- `main` and `origin/main` currently point to local StaticDuo head `4f7364064d`
- `upstream/main` points to `79a6b8f7f0` (`v1.92.0-rc.1`)

A direct merge of `upstream/main` into the local branch was attempted and aborted because it produced broad conflicts. The required strategy is now:
1. Create or use a replay branch based directly on `upstream/main`, suggested name `sync-upstream-v1.92-replay`.
2. Replay the local StaticDuo commits from `main` on top of `upstream/main` in order, preserving upstream history as the base.
3. Resolve conflicts commit-by-commit, preserving the important StaticDuo behavior.
4. Commit and push the replay branch to the user's fork only.

Local commits to preserve, in order, are the non-merge commits in `upstream/main..main` at task creation:
- `e948c79358` fix(gpt-5): respect tool_choice for models without explicit capability flag
- `79cf8cd56c` fix(azure_ai): respect tool_choice for models without explicit capability flag
- `aa529ec8ef` chore(azure): remove now-redundant tool_choice workaround in AzureOpenAIGPT5Config
- `e8eee37c16` test: add inverse regression test for gpt-5-chat tool_choice opt-out
- `c567cf7920` feat: integrate private GPT and LazyMCP changes
- `5d5fbd015c` fix(auth): handle cached user dict metadata
- `9910f5f3c4` fix: TASK-2026-05-29-001 handle dict response usage logging
- `adb408b04c` fix: normalize Responses streaming chat usage
- `cd3609df3d` fix: accept chat usage in Responses logging utils
- `e42e2cd5a0` fix: sanitize spend log null bytes
- `934b865c87` fix(auth): handle cached user dict roles
- `5526301881` fix(proxy): restore pricing and MCP auth helpers
- `7909b12b89` fix(auth): coerce cached key dicts in common checks
- `f11607cbf3` fix(auth): handle cached user dict limits
- `08a3aac163` fix(auth): use cached user dict accessor
- `feda6840ce` docs: record auth dict deploy evidence
- `ad926e49c9` chore: migrate NomadWorks artifacts to StaticEng
- `f424f1bda1` fix: TASK-2026-06-08-002 repair MCP and spend logs
- `2aaba47324` fix: TASK-2026-06-08-003 handle null MCP tool maps
- `067be69f8f` fix: TASK-2026-06-10-001 clean stale MCP delete refs
- `b4dd9e0613` fix: TASK-2026-06-11-001 make MCP delete robust
- `89cb8d2916` fix: TASK-2026-06-12-002 release onboarding claim session
- `3d814838ae` chore: TASK-2026-06-12-002 record commit evidence
- `50c1450db4` chore: TASK-2026-06-12-002 record release evidence
- `795e280a1c` chore: TASK-2026-06-12-003 commit staticeng artifacts
- `4f7364064d` chore: record staticeng closure artifacts

Important behavior to preserve:
- LazyMCP gateway endpoint and UI integration.
- LazyMCP client IP propagation in Responses/tool execution where present.
- Toolset-scoped permission enforcement and missing-server/error handling from LazyMCP review fixes where present.
- ChatGPT/private GPT provider changes from local commits.
- ChatGPT Responses streaming usage bug fix: normalize chat-style `response.usage.prompt_tokens` / `completion_tokens` to Responses-style `input_tokens` / `output_tokens` before validation/logging.
- Cached user dictionary auth fixes: metadata, roles, limits, and common check coercion.
- MCP delete robustness and null MCP tool map handling.
- Spend log null byte sanitization.
- Onboarding claim session fix.

Relevant memory findings:
- LazyMCP clean PR originally touched `mcp_server_manager.py`, `server.py`, `proxy_server.py`, `litellm_proxy_mcp_handler.py`, backend tests, `next.config.mjs`, `mcp_connect.tsx`, `mcp_servers.test.tsx`, and `mcp_servers.tsx`.
- The ChatGPT Responses usage fix was deployed in commit `07f1a4b9d5bb6c77baee64ec87e5e95a0b88535f` and normalized chat-style usage fields in `OpenAIResponsesAPIConfig.transform_streaming_response`.

## Acceptance Criteria

AC-1. The final branch is based on `upstream/main` and has StaticDuo commits replayed on top, not a broad merge where upstream is merged into the old local line.

AC-2. Upstream content from `upstream/main` is preserved unless explicitly required to reapply StaticDuo behavior.

AC-3. LazyMCP functionality remains present in backend routing, Responses MCP handling, and dashboard MCP UI surfaces.

AC-4. ChatGPT/private GPT provider behavior and the Responses usage normalization bug fix remain present.

AC-5. Cached-user auth dictionary fixes, MCP delete robustness, null MCP tool map handling, spend log null byte sanitization, and onboarding claim-session behavior remain present or are verified already incorporated upstream.

AC-6. All merge/cherry-pick conflicts are resolved with no leftover conflict markers and no unresolved index entries.

AC-7. Targeted verification is run for the highest-risk touched areas, especially LazyMCP/MCP, Responses usage, auth cached dicts, and onboarding where feasible. Any skipped or infeasible verification must be explicitly justified.

AC-8. The replay branch is pushed to `origin` (the user's fork) and not pushed to `upstream`.

AC-9. The worktree ends clean, or any residual dirty state is explicitly reported.

AC-10. No secrets, `.env` contents, passwords, API keys, tokens, cookies, private keys, or session tokens are committed or logged.

## Expected Evidence

Create `.staticeng/evidences/TASK-2026-07-07-001-sync-upstream-v192-replay/` with:
- `SUMMARY.md` mapping each AC to evidence.
- `logs/` containing pre-status, branch creation, cherry-pick/rebase steps, conflict summaries/resolutions, verification commands, push output, and final status.
- Screenshots are not required unless UI manual verification is performed; if performed, place them under `screenshots/`.

## Handoff

[Agent Message] From: product_manager To: workflow_runner
Please execute the upstream sync using a replay strategy. Do not re-run the aborted merge strategy. Base the result on `upstream/main`, replay the listed StaticDuo commits on top, resolve conflicts commit-by-commit, and prioritize preserving LazyMCP, private GPT/ChatGPT fixes, Responses usage normalization, cached-user auth dict fixes, MCP delete robustness, spend log null-byte sanitization, and onboarding claim-session behavior. Prefer upstream code when upstream already contains equivalent behavior; otherwise reapply the smallest local change needed. Push only to `origin`, never to `upstream`. Produce the required evidence packet and return Summary, Work Performed, Acceptance Criteria Coverage, Documentation Impact, Open Risks, and Recommended Next Step.

## Reopen History

- 2026-07-07: QA reopened same-scope because `python -m py_compile litellm/proxy/_experimental/mcp_server/mcp_server_manager.py` failed with `SyntaxError: invalid syntax` at line 4016. The syntax error blocked Proxy/MCP/auth/spend/onboarding pytest collection.
- 2026-07-07: QA reopened same-scope after dependency sync for three targeted failures: LazyMCP shutdown left `_lazy_session_manager_cm` out of the session manager globals/lifecycle; cached-user SCIM dict coverage patched stale `user_api_key_auth.get_key_object` after upstream auth resolver refactor; MCP partial-update null map tests had contradictory expectations for explicit `null` tool override maps.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

- Fixed the replay conflict fallout in `litellm/proxy/_experimental/mcp_server/mcp_server_manager.py` by restoring the missing `try:` block around each DB MCP server rebuild in `reload_servers_from_database` and dedenting the rebuild path out of the reused-server `continue` branch.
- Preserved the staged reload behavior: unchanged servers are reused, changed/new servers are rebuilt with encrypted env var handling, short prefixes are carried forward, and per-server rebuild failures are logged without aborting the full registry reload.
- Verification recorded in `.staticeng/evidences/TASK-2026-07-07-001-sync-upstream-v192-replay/logs/17-developer-reopen-fix.log`.
- Fixed the dependency-sync targeted failures: LazyMCP session manager init/shutdown now declares and enters/exits `_lazy_session_manager_cm`; the cached-user SCIM dict regression patches `IdentityStore._resolve_key`, matching upstream's resolver seam while preserving dict metadata rejection behavior; and the older null-map test now matches the preserved behavior where explicit `null` map fields are ignored while explicit `{}` clears overrides.
- Verification recorded in `.staticeng/evidences/TASK-2026-07-07-001-sync-upstream-v192-replay/logs/40-developer-fix-targeted-failures.log`.
