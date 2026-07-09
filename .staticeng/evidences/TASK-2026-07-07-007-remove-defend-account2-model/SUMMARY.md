# TASK-2026-07-07-007 Evidence Summary

## Result

Completed. The mistaken `defend-account2/gpt-5.5` deployment was removed from the local/NAS LiteLLM database and router. `defend/gpt-5.5` remains present, and the required `chatgpt-account2/*` deployments remain present with `chatgpt_auth_profile = account2` in the database.

## Removal method

Used the running local/NAS `litellm` container's LiteLLM admin API, not a direct SQL delete:

- Endpoint: `POST /model/delete`
- URL used from inside container: `http://127.0.0.1:4000/model/delete`
- Target model: `defend-account2/gpt-5.5`
- Target model id: `7f239a33-28d4-4d6c-953d-ea8ed5dad661`
- Response: HTTP 200, `{"message":"Model: 7f239a33-28d4-4d6c-953d-ea8ed5dad661 deleted successfully"}`

This path removed the database row and updated the in-memory router without a rebuild, redeploy, or container restart.

## Verification

- Direct DB pre-check showed `defend-account2/gpt-5.5` existed before removal with `chatgpt_auth_profile = account2`.
- Direct DB post-check no longer returns `defend-account2/gpt-5.5`.
- Direct DB post-check still returns `defend/gpt-5.5` with no `chatgpt_auth_profile` override.
- Direct DB post-check still returns all required `chatgpt-account2/*` deployments with `chatgpt_auth_profile = account2`.
- `GET /model/info` returned HTTP 200 and no longer shows `defend-account2/gpt-5.5`.
- `GET /model/info` still shows `defend/gpt-5.5` and all required `chatgpt-account2/*` deployments.
- `/health/readiness` returned HTTP 200 with DB connected.
- `/health/liveliness` returned HTTP 200.
- Docker health for `/litellm` is `healthy`.
- No live ChatGPT model invocation, ChatGPT login, or auth refresh was performed.

## Acceptance Criteria

- AC-1: Passed. `defend-account2/gpt-5.5` is absent from direct DB inspection and `/model/info` after removal.
- AC-2: Passed. `defend/gpt-5.5` remains present in direct DB inspection and `/model/info`.
- AC-3: Passed. The required `chatgpt-account2/gpt-5.3-codex`, `chatgpt-account2/gpt-5.3-codex-spark`, `chatgpt-account2/gpt-5.4`, `chatgpt-account2/gpt-5.4-mini`, and `chatgpt-account2/gpt-5.5` rows remain present with `chatgpt_auth_profile = account2` in the database.
- AC-4: Passed. LiteLLM readiness, liveliness, and Docker health checks passed after removal.
- AC-5: Passed. Evidence packet exists at `.staticeng/evidences/TASK-2026-07-07-007-remove-defend-account2-model/` with this `SUMMARY.md` and safe logs under `.staticeng/evidences/TASK-2026-07-07-007-remove-defend-account2-model/logs/`.

## Logs

- `.staticeng/evidences/TASK-2026-07-07-007-remove-defend-account2-model/logs/pre_removal_db.log`
- `.staticeng/evidences/TASK-2026-07-07-007-remove-defend-account2-model/logs/removal.log`
- `.staticeng/evidences/TASK-2026-07-07-007-remove-defend-account2-model/logs/post_removal_db.log`
- `.staticeng/evidences/TASK-2026-07-07-007-remove-defend-account2-model/logs/post_removal_api_health.log`
- `.staticeng/evidences/TASK-2026-07-07-007-remove-defend-account2-model/logs/container_health.log`

## Notes and risks

- `GET /model/info` redacts sensitive LiteLLM parameters, so exact `chatgpt_auth_profile` values were verified by direct DB inspection.
- No rebuild, redeploy, restart, commit, or application code change was performed.
