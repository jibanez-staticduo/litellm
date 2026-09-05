# Isolated baseline review and checkpoint

Baseline: detached worktree `/tmp/opencode/task0905-baseline`, exact unpatched HEAD `2b3123c667b13ff0765ed6cc26d00eb6743d2458`. Working main matched origin/main after fetch (0 ahead, 0 behind)

Both runs used the existing Python 3.13 venv, explicit `/usr/bin/env -i`, synthetic HOME, `PYTHON_DOTENV_DISABLED=1`, local model-cost map and `/usr/bin/unshare -Urn` network isolation. No inherited provider configuration or credential was available. Mocked Responses tests received only `OPENAI_API_KEY=synthetic-test-key`. The bare `env` command resolves to a local wrapper and did not execute the initial attempts; only explicit /usr/bin/env results count

## Fifteen original failures

Five cache/input-shape failures passed unchanged in both source trees. Combined request-body, Responses utilities and MCP handler files: baseline 113 passed/1 failed in 46.26s; patched 113 passed/1 failed in 44.31s. These five failures came from inherited endpoint settings, which intentionally disable native OpenAI cache markers for custom gateways. No cache-policy product change was justified

The remaining shape failure was identical on both trees: one malformed LazyMCP map assertion omitted `toolset_id=None`. `_LazyMcpToolServerMap` requires the field, the decoder consistently supplies it, neighboring malformed-input assertions already require it, and callers read it as an optional scope. Corrected the one stale expectation without changing the decoder, server selection or permissions. Imports in that touched product test were sorted to satisfy direct Ruff checks

The nine provider-dependent cases also reproduced on both trees with networking unavailable and no credentials: speech iterator, image generation False/True, moderation None/bare/prefixed model, pass-through moderation, rerank and transcription. Both runs returned 9 failed, 1 passed, 165 deselected; baseline 12.74s, patched 12.96s. The extra passing case was selected by the name expression. Existing rerun plugin was disabled for these classification runs, producing two unknown-flaky-marker warnings. These failures are unavailable external integration coverage, not successful tests and not proof of product regression

No maintenance-tool finding was fixed, and no global security or harness change was made

## Relevant product verification

The exact memory fix projects five session attributes instead of recursively serializing GenericLiteLLMParams. The profile fix restores `chatgpt_auth_profile`, `chatgpt_token_dir` and `chatgpt_auth_file` to existing sparse optional-parameter extraction. Reviewed all six changed product/source/test/CodeMap paths

Network-isolated focused matrix: all ChatGPT tests, mapped get_litellm_params tests, full Responses request-body and utilities files, and full Responses MCP handler file: **229 passed, no skips, four existing fork/multiprocessing warnings, 80.07 seconds**

The first isolated focused run found three authenticator fixture failures because the synthetic HOME lacked the lock-file parent directory while the fixture mocks directory creation. Creating only that empty test directory resolved them; no authenticator source/test change was made. A broader 773-case run had previously been interrupted at the 180-second command limit and is not reported as a completed result

The prior broad result remains 964 passed/15 failed, not an all-pass claim. No new product regression was found in the baseline comparison. The two maintenance lint findings remain out of scope. PMA explicitly permits the product-only checkpoint and contained Fedora build/deployment after relevant direct checks

## Next gate

Commit only reviewed product fixes, technical invariants, same-task task/evidence and the corrected product assertion. Non-force push main, build the exact clean commit using the existing Dockerfile, then verify the real Fedora Chat/Responses/MCP/LazyMCP matrix and 900-second stability. Until those live gates pass, task stays active and NAS is prohibited
