---
id: DISCUSSION-002
title: "Investigate multi-account ChatGPT subscription auth in LiteLLM"
status: closed
summarized_by: business_analyst
source: runtime-transcript
---

# Discussion Summary

## Topic
Investigate whether LiteLLM can support multiple ChatGPT subscription authentication contexts under separate provider/model prefixes.

## Purpose
The user wants one LiteLLM instance to route to multiple different ChatGPT subscription accounts, each with separate tokens, refresh tokens, and session data, instead of the apparent current limitation of a single ChatGPT subscription auth context.

## Repository Truth Relevant To This Discussion
- Repository path: `/home/staticduo/git/litellm`.
- Current fork convention: `origin` points to `git@github.com:jibanez-staticduo/litellm.git`; `upstream` points to `https://github.com/BerriAI/litellm`.
- Current `main`/`origin/main` is the upstream replay line based on `upstream/main` at `79a6b8f7f0` (`v1.92.0-rc.1`), with StaticDuo commits replayed on top.
- Old main is preserved at `backup-main-before-upstream-v1.92` at `4f7364064d`.
- Known good deployed image: `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-cachecodecfix-20260707`.
- Known good digest: `docker.staticduo.com/litellm@sha256:23f346521079a27dfeb9039e73dc2328c268ec50d44e11dc662c33d78a006d86`.
- Local/NAS stack path: `/volume2/docker/litellm`.
- Fedora stack path: `/home/staticduo/docker/litellm` via SSH host `fedora`.
- Release script: `/home/staticduo/git/release-litellm.sh`.
- `staticeng_validate` is currently known to fail because of StaticEng metadata/CodeMap debt, not functional LiteLLM release issues: broken links in `.staticeng/codemap.yml` and many missing `codemap.yml` files across source directories.
- Existing local features/fixes to preserve while changing auth behavior include LazyMCP, ChatGPT/private GPT, Responses usage, auth/cache, MCP, spend, and onboarding fixes.
- Recent release blocker `NameError: CacheCodec is not defined` was fixed by importing `CacheCodec` in `litellm/proxy/proxy_server.py`, with regression test `test_update_cache_serializes_cached_user_and_team_spend`.
- Local/NAS and Fedora deployments of the known good image are healthy; readiness returns `{"status":"healthy","db":"connected"}`, liveliness returns `"I'm alive!"`, LazyMCP/MCP smoke checks pass, and post-deploy logs are clean.

## Facts Established
- The user believes LiteLLM's current ChatGPT subscription auth may only allow one authentication context for the `chatgpt` provider.
- The user wants to configure multiple ChatGPT subscription-backed providers in one LiteLLM instance, using names such as `chatgpt`, `chatgpt2`, `chatgpt3`, and `chatgpt4`.
- Desired model examples include separate model prefixes such as `chatgpt/gpt-5.5` and `chatgpt2/gpt-5.5`, where each prefix maps to a different ChatGPT subscription account.
- Each ChatGPT provider/account must maintain distinct tokens, refresh tokens, and session data.
- The user suspects the ChatGPT login/auth flow is initiated or completed through log output, because login may require opening a link shown in logs.
- The user suspects ChatGPT subscription auth might be implemented as an external-ish plugin or component, which could make multi-token or multi-refresh-token support easier.
- No implementation design has been validated yet.

## Requirements Captured
- Investigate how LiteLLM implements ChatGPT subscription authentication.
- Determine whether the current implementation is globally single-account or can already support multiple independent auth contexts.
- Identify where ChatGPT subscription tokens, refresh tokens, and session data are loaded, stored, refreshed, cached, and selected per request.
- Identify whether provider/model naming can support aliases such as `chatgpt2/gpt-5.5` while still routing through ChatGPT subscription auth.
- If multi-account support is not present, define a workflow-ready implementation approach for multiple independent ChatGPT subscription auth contexts in one LiteLLM process.
- Preserve existing deployed behavior and StaticDuo fork features while investigating or planning changes.
- Keep secrets out of logs, evidence, summaries, commits, and chat output.

## Constraints
- Do not expose `.env`, master keys, API keys, tokens, cookies, private keys, refresh tokens, session tokens, or auth URLs that could grant access.
- The existing known good deployed image and release state must remain rollback-safe.
- Upstream history strategy must remain intact: base work on the current replay line rather than merging upstream into old local history.
- Any future implementation must avoid regressing LazyMCP, ChatGPT/private GPT, Responses usage, auth/cache, MCP, spend, and onboarding behavior.
- StaticEng validation failures from CodeMap/link debt should not be confused with functional LiteLLM auth/deploy failures.
- Investigation should not assume the user's interpretation is correct; it must verify current behavior in source/config/runtime docs first.

## Non-Goals
- Do not implement the multi-account ChatGPT auth change as part of this discussion-summary task.
- Do not rotate, print, or collect real ChatGPT tokens or refresh tokens in the discussion artifact.
- Do not perform a new release/deploy as part of this summary task.
- Do not clean up unrelated StaticEng CodeMap/link debt as part of this discussion unless PMA creates a separate task.
- Do not change provider/model naming semantics until the current ChatGPT auth architecture is understood.

## Decisions Made
- The immediate workflow need is investigation and requirements clarification, not implementation.
- The desired product direction is one LiteLLM instance supporting multiple ChatGPT subscription accounts under distinct provider/model prefixes if technically feasible.
- Unresolved implementation details must be captured as open questions rather than guessed.

## Assumptions
- The user has or will have multiple legitimate ChatGPT subscription accounts whose auth contexts they want to use independently.
- The user expects model/provider prefixes such as `chatgpt2` to behave as separate provider identities, not merely aliases sharing the same auth state.
- The current deployed StaticDuo LiteLLM fork includes local ChatGPT/private GPT subscription-related behavior that may not match upstream exactly.
- The login-link-in-logs behavior may be part of the current ChatGPT subscription auth flow, but this must be verified in code or runtime documentation.

## Open Questions
- Where exactly is ChatGPT subscription auth implemented in this fork: core LiteLLM provider code, proxy startup/config, plugin-like external module, or another integration layer?
- Is the ChatGPT subscription auth state currently stored globally, per provider, per model deployment, per process, or in another scope?
- How are access tokens, refresh tokens, cookies/session data, and account identifiers represented and refreshed today?
- Does LiteLLM's provider registry or model routing support arbitrary ChatGPT-like provider prefixes such as `chatgpt2`, or would this require provider alias/namespace changes?
- Can multiple auth sessions safely coexist in one process without shared global caches, singleton clients, environment variables, or file paths colliding?
- How does login currently work, and is the user correct that a login URL is emitted through logs?
- What config shape should represent multiple ChatGPT subscription accounts without exposing secrets and without breaking existing single-account setups?
- Are there upstream constraints, terms, rate limits, or anti-abuse mechanisms that affect using multiple ChatGPT subscription accounts from one LiteLLM instance?
- What tests and live validation should prove separate accounts are selected correctly per provider prefix?

## Risks Or Concerns
- Shared global auth state could cause requests for `chatgpt2` to accidentally use the primary `chatgpt` account.
- Token/refresh-token handling is high risk because logs, evidence, or debug output could leak credentials.
- Login flows that rely on URLs emitted in logs may be difficult to support cleanly for multiple accounts without confusing operators.
- Refresh-token race conditions or cache key collisions could corrupt one account's session using another account's credentials.
- Provider alias changes could unintentionally affect model routing, spend logging, auth/cache behavior, or existing ChatGPT/private GPT support.
- Upstream changes from the replayed v1.92 line may have modified ChatGPT auth behavior compared with older StaticDuo code.
- StaticEng validation noise from unrelated CodeMap debt could obscure real investigation or test failures if not clearly separated.

## Referenced Files Or Areas
- `/home/staticduo/git/litellm`
- `/volume2/docker/litellm`
- `/home/staticduo/docker/litellm`
- `/home/staticduo/git/release-litellm.sh`
- `litellm/proxy/proxy_server.py`
- `.staticeng/evidences/TASK-2026-07-07-001-sync-upstream-v192-replay/SUMMARY.md`
- `.staticeng/evidences/TASK-2026-07-07-003-deploy-litellm-fedora/SUMMARY.md`
- `.staticeng/tasks/done/TASK-2026-07-07-003-deploy-litellm-fedora.md`
- `.staticeng/codemap.yml`
- ChatGPT/private GPT provider implementation areas to be located during investigation
- LiteLLM provider registry, model routing, auth/cache, token refresh, and session persistence areas to be located during investigation

## Recommended Workflow Next Step
- assigned_to: technical_architect
- why: The next step is an architecture investigation of the existing ChatGPT subscription auth flow, provider/model routing, and state scoping before PMA decomposes implementation tasks or approves behavior changes.
