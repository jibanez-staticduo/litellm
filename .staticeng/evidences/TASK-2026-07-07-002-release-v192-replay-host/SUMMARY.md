# Evidence Summary: TASK-2026-07-07-002-release-v192-replay-host

## Result

Release attempt built and deployed `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-20260707`, but post-deploy logs exposed a release-blocking regression: `NameError: CacheCodec is not defined` in `proxy_server.py` spend tracking cache update paths. Because this can leave budget enforcement using stale spend values, the release was rolled back.

Production is currently stable on rollback image `docker.staticduo.com/litellm:rollback-20260707-131635`.

## Images

- Attempted release image: `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-20260707`
- Attempted release digest: `docker.staticduo.com/litellm@sha256:0fc09c92eb4706def0d3c8cd6f1c67ff4b4364ce9a6aa9af995b1bf244ed0363`
- Attempted release image id: `sha256:201b6e3b60ce73d2bcc5bb49b5d7820126ba18eee4e7c823830634cc1fc4a94e`
- Rollback image: `docker.staticduo.com/litellm:rollback-20260707-131635`
- Rollback digest: `sha256:102158c62182f4db494be543dbb09580b4074dd69f87967a15e77ba3a5349a79`

## Acceptance Criteria Coverage

- AC-1: PASS. Release ran from `/home/staticduo/git/litellm` `main`; code content was the replay line. One StaticEng-only preflight commit existed on top to clean the worktree before release.
- AC-2: PASS. Image built and pushed successfully; see `logs/04-release-retry.log`.
- AC-3: PASS. Rollback tag was created and pushed by the release script; see `logs/04-release-retry.log` and `logs/06-rollback.log`.
- AC-4: FAIL then ROLLED BACK. The new image deployed and served readiness, but logs showed the `CacheCodec` spend tracking regression. Production now runs rollback image and is healthy; see `logs/07-rollback-verification.log`.
- AC-5: PASS. Fedora deploy was explicitly skipped; see `logs/04-release-retry.log`.
- AC-6: PARTIAL PASS. New image readiness/liveliness passed and LazyMCP smoke succeeded, but recent logs exposed the release-blocking spend cache regression.
- AC-7: PASS. Rollback was performed after the regression was observed.
- AC-8: PASS. Evidence logs are present under `logs/`.
- AC-9: PENDING until this evidence and blocker state are committed/pushed.
- AC-10: PASS. Evidence does not include `.env` contents, master keys, API keys, tokens, cookies, private keys, or session tokens.

## Blocker

`litellm/proxy/proxy_server.py` references `CacheCodec` in spend cache update paths, but the deployed build does not have `CacheCodec` defined in that module scope. Runtime warnings observed after live requests:

```text
Spend tracking - failed to update user spend in cache. Budget enforcement may use stale spend values. ... name 'CacheCodec' is not defined
Spend tracking - failed to update team spend in cache. Budget enforcement may use stale spend values. ... name 'CacheCodec' is not defined
```

Static source search confirms `proxy_server.py` uses `CacheCodec` but does not import it, while other modules import it from `litellm.proxy.common_utils.cache_pydantic_utils`.

## Current Production State

- Container: `litellm`
- Image: `docker.staticduo.com/litellm:rollback-20260707-131635`
- Docker status: running, healthy
- `/health/readiness`: `200 {"status":"healthy","db":"connected"}`
- `/health/liveliness`: `200 "I'm alive!"`

## Recommended Next Step

Fix the missing `CacheCodec` import/availability in `litellm/proxy/proxy_server.py`, run targeted spend/auth/cache tests, build a new image, and retry the local release.

## Reopen Pre-Release Fix Verification

- Code fix: `litellm/proxy/proxy_server.py` now imports `CacheCodec` from `litellm.proxy.common_utils.cache_pydantic_utils`.
- Regression coverage: `tests/test_litellm/proxy/proxy_server/test_spend_counters.py::test_update_cache_serializes_cached_user_and_team_spend` verifies cached user/team spend updates serialize into the cache pipeline, which would have failed when `CacheCodec` was missing from `proxy_server.py` module scope.
- Static/import verification: `.venv/bin/python -m py_compile litellm/proxy/proxy_server.py` and a focused import assertion passed; see `logs/08-py-compile.log` and `logs/09-cachecodec-import-check.log`.
- Targeted tests: `.venv/bin/python -m pytest tests/test_litellm/proxy/common_utils/test_cache_codec.py tests/test_litellm/proxy/proxy_server/test_spend_counters.py -q` passed with 63 tests; see `logs/11-targeted-pytest-cachecodec-and-spend.log`.
- Targeted symbol lint: `.venv/bin/ruff check --select F401,F821 litellm/proxy/proxy_server.py tests/test_litellm/proxy/proxy_server/test_spend_counters.py` passed; see `logs/14-targeted-ruff-cachecodec-symbols.log`.
- `make pre-commit` was attempted and failed on repository-wide ruff strict budget overage relative to `origin/litellm_internal_staging`; this appears pre-existing to the CacheCodec fix and is summarized in `logs/12-make-pre-commit-summary.log`.

## Reopen Acceptance Criteria Coverage

- AC-11: PASS pre-release. `CacheCodec` is available in `proxy_server.py` spend tracking cache update paths via a minimal import.
- AC-12: PASS pre-release. A focused regression now exercises cached user/team spend serialization through `update_cache`.
- AC-13: PENDING. The code fix, pre-release task state, and evidence must be committed before retrying the release.
- AC-14: PENDING. Retry must use `staticduo-gpt-lazymcp-v1.92-replay-cachecodecfix-20260707`.
- AC-15: PENDING. Retry must remain local-host-only and push only to `origin`.
- AC-16: PENDING. Final production state must be verified after retry or rollback.
