---
id: DISCUSSION-002
title: "Release ChatGPT auth profiles image and add account2 DB models"
status: closed
summarized_by: product_manager
source: runtime-transcript
---

# Discussion Summary

## Topic
Release the LiteLLM image containing ChatGPT auth profile support to the local/NAS LiteLLM stack and add account2 ChatGPT deployments directly in the LiteLLM database.

## User Requirements
- Keep existing default ChatGPT auth as `auth.json` so reverting to an official image keeps the primary account working.
- Do not rename existing `auth.json` to `account1.json`.
- Add account2 models by database mutation.
- Mirror existing regular ChatGPT deployments for account2.
- Do not perform account2 ChatGPT login yet; user will do that later.
- Deploy only on this host/local NAS stack, not Fedora.

## Decisions
- Use the new `chatgpt_auth_profile: account2` feature rather than adding a new provider named `chatgpt2`.
- Keep regular ChatGPT deployments with default auth/no account2 profile.
- Build and deploy a new local image from commit `6ccc6ae919` containing TASK-2026-07-07-005.
- Add account2 deployments directly to `LiteLLM_ProxyModelTable`.

## Outcome
- New local image deployed: `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-chatgptprofiles-20260708`.
- Digest: `docker.staticduo.com/litellm@sha256:a9bb7c0865dd3b65c1065c87061c3ca6bbfc7d50033aeba28ad43b7b6bdd895f`.
- Rollback tag: `docker.staticduo.com/litellm:rollback-20260708-003315`.
- Added account2 deployments:
  - `chatgpt-account2/gpt-5.3-codex`
  - `chatgpt-account2/gpt-5.3-codex-spark`
  - `chatgpt-account2/gpt-5.4`
  - `chatgpt-account2/gpt-5.4-mini`
  - `chatgpt-account2/gpt-5.5`
  - `defend-account2/gpt-5.5`

## Verification
- Container `litellm` runs the new image and reports Docker health `healthy`.
- Internal readiness and liveliness checks returned HTTP 200.
- `/model/info` shows all original regular and account2 deployments.
- Direct DB verification shows account2 rows have `chatgpt_auth_profile = account2` and regular rows have no account2 override.
- Existing `auth.json` remains present and `account2.json` is absent because login was not performed.

## Follow-Up
- User should trigger/login account2 later by using an account2 model and completing the device-code login from logs.
- If exact `chatgpt2/*` names are desired, add aliases or rename account2 rows in a separate DB operation.
