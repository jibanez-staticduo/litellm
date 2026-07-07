---
id: TASK-2026-07-07-006-release-chatgpt-profiles-local-and-add-account2-models
complexity: standard
track: implementation
slice: foundation
status: done
scr: SCR-2026-07-07-001-chatgpt-auth-profiles
parent: null
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-07-07-006 - Release ChatGPT Profiles Locally and Add Account2 DB Models

## Classification
- **complexity:** standard
- **track:** implementation
- **slice:** foundation

## Objective
Build a new LiteLLM image from the current `main` containing ChatGPT auth profiles, deploy it to the local/NAS LiteLLM stack on this host, and add account2 ChatGPT model deployments directly in the LiteLLM database by cloning the current regular ChatGPT deployments and adding `chatgpt_auth_profile: account2`.

## User Requirements
- Deploy on this host only; do not deploy to Fedora in this task.
- Keep the existing default ChatGPT auth as `auth.json`; do not rename or move it.
- Add account2 models by database mutation, not by only editing static config.
- account2 should mirror the existing regular ChatGPT models as closely as possible, but with separate user-facing names and `chatgpt_auth_profile: account2`.
- Do not perform ChatGPT account2 login yet; the user will complete login later.

## Scope
- Build and tag a new image from commit `6ccc6ae919` or later `main` containing TASK-2026-07-07-005.
- Deploy the new image to the local/NAS LiteLLM stack at `/volume2/docker/litellm` using the existing release/deploy workflow where possible.
- Inspect current regular ChatGPT deployments via database/API as needed, without exposing credentials.
- Mutate the LiteLLM database to add account2 deployments modeled after the current regular ChatGPT deployments.
- Verify container health and model registration.
- Do not expose `.env`, master keys, API keys, tokens, cookies, private keys, auth files, refresh tokens, or session tokens.

## Acceptance Criteria
- [x] AC-1: New local image is built from current `main` and pushed/tagged in the local registry with a rollback reference captured.
- [x] AC-2: Local/NAS LiteLLM container is running the new image and passes readiness/liveliness checks.
- [x] AC-3: Existing regular ChatGPT deployments remain present and continue to use default auth behavior (`auth.json`, no `chatgpt_auth_profile: account2`).
- [x] AC-4: Account2 ChatGPT deployments exist in the LiteLLM database, mirror the current regular ChatGPT deployments, and include `chatgpt_auth_profile: account2`.
- [x] AC-5: Account2 deployments are visible through LiteLLM model inspection after deployment/reload/restart.
- [x] AC-6: No ChatGPT login is performed; missing account2 auth should be left for the user to complete later.
- [x] AC-7: Evidence packet exists under `.staticeng/evidences/TASK-2026-07-07-006-release-chatgpt-profiles-local-and-add-account2-models/` with `SUMMARY.md` and safe logs.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-07-07-006-release-chatgpt-profiles-local-and-add-account2-models/` containing:
- `SUMMARY.md` mapping AC-1 through AC-7 to results.
- `logs/` with safe command outputs for release/build, deployment, health checks, database inspection/mutation summary, and model inspection.
- Redact or omit any secret values.

## Active Discussions
- DISCUSSION-002: Release ChatGPT auth profiles image and add account2 DB models

## Handoff
[Agent Message] From: product_manager To: developer

Please execute this operational implementation task. Start with read-only preflight: confirm git/worktree safety, current image/container, and current regular ChatGPT deployments. Then build/deploy the new image locally only and add account2 deployments directly in the LiteLLM database. Keep the existing `auth.json` default untouched. Do not run account2 login. Capture rollback info and safe evidence. If direct database mutation is unsafe or the schema is unclear, stop and report the safest SQL/API-equivalent plan before writing.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

### Summary
- Built and deployed local/NAS image `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-chatgptprofiles-20260708` from commit `6ccc6ae91940406cc6ce806eb2d9997c9e9dc39c`.
- Image digest: `docker.staticduo.com/litellm@sha256:a9bb7c0865dd3b65c1065c87061c3ca6bbfc7d50033aeba28ad43b7b6bdd895f`.
- Rollback tag: `docker.staticduo.com/litellm:rollback-20260708-003315`.
- Added account2 DB deployments via direct Prisma `execute_raw` inserts into `LiteLLM_ProxyModelTable`.

### Account2 Models Added
- `chatgpt-account2/gpt-5.3-codex`
- `chatgpt-account2/gpt-5.3-codex-spark`
- `chatgpt-account2/gpt-5.4`
- `chatgpt-account2/gpt-5.4-mini`
- `chatgpt-account2/gpt-5.5`
- `defend-account2/gpt-5.5`

### Verification
- Docker container `litellm` is running the new image and reports health `healthy`.
- Internal `/health/readiness` returned HTTP 200 with DB connected.
- Internal `/health/liveliness` returned HTTP 200.
- `/model/info` shows all regular and account2 models.
- Direct DB verification confirms regular rows have no account2 profile and account2 rows have `chatgpt_auth_profile = account2`.
- `auth.json` remains present; `account2.json` remains absent because login was not performed.

## PMA Final Closure

### Acceptance Criteria Coverage
- AC-1 through AC-7 are satisfied by the evidence summary and logs.
- PMA rechecked container image/health status and internal readiness/liveliness.

### Documentation Impact
- No product docs were changed; operational state is captured in task evidence.

### Open Risks
- Account2 auth still needs user login before first successful real account2 model call.
- User-facing model names were added as `chatgpt-account2/*` and `defend-account2/*`; exact `chatgpt2/*` aliases can be added separately if desired.
- `staticeng_validate` still fails due pre-existing CodeMap/link debt unrelated to this task.
