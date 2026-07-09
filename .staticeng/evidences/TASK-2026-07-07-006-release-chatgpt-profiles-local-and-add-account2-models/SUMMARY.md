# TASK-2026-07-07-006 Evidence Summary

## Result

Completed local/NAS-only release and database model addition for ChatGPT account2 profiles. No application code was modified and no Fedora deployment was performed.

## Release

- Source commit: `6ccc6ae91940406cc6ce806eb2d9997c9e9dc39c`
- Image tag: `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-chatgptprofiles-20260708`
- Image digest: `docker.staticduo.com/litellm@sha256:a9bb7c0865dd3b65c1065c87061c3ca6bbfc7d50033aeba28ad43b7b6bdd895f`
- Local container: `litellm`
- Local stack path: `/volume2/docker/litellm`
- Rollback image tag created: `docker.staticduo.com/litellm:rollback-20260708-003315`
- Rollback digest: `docker.staticduo.com/litellm@sha256:23f346521079a27dfeb9039e73dc2328c268ec50d44e11dc662c33d78a006d86`
- Prior known-good image: `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-cachecodecfix-20260707`

## Database mutation

Mutation method: direct database insert through the LiteLLM container's Prisma client using `execute_raw` into `"LiteLLM_ProxyModelTable"`. Source rows were cloned, new `model_id` values were generated, and `litellm_params.chatgpt_auth_profile` was set to `account2` on the account2 rows only.

Added models:

- `chatgpt-account2/gpt-5.3-codex` from `chatgpt/gpt-5.3-codex`
- `chatgpt-account2/gpt-5.3-codex-spark` from `chatgpt/gpt-5.3-codex-spark`
- `chatgpt-account2/gpt-5.4` from `chatgpt/gpt-5.4`
- `chatgpt-account2/gpt-5.4-mini` from `chatgpt/gpt-5.4-mini`
- `chatgpt-account2/gpt-5.5` from `chatgpt/gpt-5.5`
- `defend-account2/gpt-5.5` from `defend/gpt-5.5`

## Verification

- Container is running the new image and reports Docker health `healthy`.
- `/health/readiness` returned HTTP 200 with DB connected.
- `/health/liveliness` returned HTTP 200.
- `GET /model/info` shows all original regular ChatGPT deployments and all six account2 deployments.
- Direct DB verification confirms regular rows have no `chatgpt_auth_profile` override and account2 rows have `chatgpt_auth_profile = account2`.
- `auth.json` remains present; `account2.json` is absent, which is expected because no ChatGPT account2 login was performed.
- No live ChatGPT model invocation was run.

## Acceptance Criteria

- AC-1: Passed. New image built from `6ccc6ae91940406cc6ce806eb2d9997c9e9dc39c`, pushed with digest captured, and rollback reference captured.
- AC-2: Passed. Local/NAS `litellm` container runs the new image and health checks pass.
- AC-3: Passed. Existing regular ChatGPT deployments remain present and direct DB verification shows no account2 profile on regular rows.
- AC-4: Passed. Six account2 deployments exist in the database and have `chatgpt_auth_profile = account2`.
- AC-5: Passed. Account2 deployments are visible through `/model/info` after restart.
- AC-6: Passed. No ChatGPT login or live ChatGPT invocation was performed; `account2.json` remains absent.
- AC-7: Passed. Evidence packet includes this summary and safe logs under `.staticeng/evidences/TASK-2026-07-07-006-release-chatgpt-profiles-local-and-add-account2-models/logs/`.

## Logs

- `.staticeng/evidences/TASK-2026-07-07-006-release-chatgpt-profiles-local-and-add-account2-models/logs/preflight_and_rollback.log`
- `.staticeng/evidences/TASK-2026-07-07-006-release-chatgpt-profiles-local-and-add-account2-models/logs/release_build_deploy.log`
- `.staticeng/evidences/TASK-2026-07-07-006-release-chatgpt-profiles-local-and-add-account2-models/logs/container_image_and_auth_files.log`
- `.staticeng/evidences/TASK-2026-07-07-006-release-chatgpt-profiles-local-and-add-account2-models/logs/db_mutation.log`
- `.staticeng/evidences/TASK-2026-07-07-006-release-chatgpt-profiles-local-and-add-account2-models/logs/restart_after_db_mutation.log`
- `.staticeng/evidences/TASK-2026-07-07-006-release-chatgpt-profiles-local-and-add-account2-models/logs/final_verification.log`

## Notes and risks

- `GET /model/info` redacts `chatgpt_auth_profile` as a sensitive/banned parameter, so exact profile values were verified directly in the database.
- The account2 auth file is intentionally not present yet. First use after the user completes account2 login should create/use `account2.json`.
