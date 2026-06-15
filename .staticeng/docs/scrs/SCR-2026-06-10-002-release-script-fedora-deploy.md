---
scr_id: SCR-2026-06-10-002-release-script-fedora-deploy
status: approved
owner: product_manager
created: 2026-06-10
related_task: TASK-2026-06-10-002-update-release-script-fedora
---

# SCR-2026-06-10-002: Release Script Fedora Deployment

## Problem

`/home/staticduo/git/release-litellm.sh` builds and deploys the LiteLLM image to the NAS stack at `/volume2/docker/litellm`, but the user also runs a Fedora LiteLLM stack at `fedora:/home/staticduo/docker/litellm`. Releases should update both deployments from the same image tag.

## Approved Behavior

When `DEPLOY=1`, the release script must continue updating the local NAS stack and also update the Fedora stack over SSH. The Fedora update should set `LITELLM_IMAGE` in the remote stack `.env`, pull the new image, and run `docker compose up -d litellm` for the remote stack. Fedora deployment must be configurable and disable-able.

## Scope

In scope:
- Add configurable Fedora deployment variables to `release-litellm.sh`.
- Preserve existing NAS behavior.
- Keep `--build-only` behavior as no deploy.
- Add an opt-out for Fedora deploy.
- Verify shell syntax and safe remote command behavior.

Out of scope:
- Direct production DB changes.
- Changing the LiteLLM app code beyond the existing MCP fix.
- Redesigning the release process.

## Acceptance Criteria

AC-1. `release-litellm.sh` has configurable Fedora host and stack directory defaults: `fedora` and `/home/staticduo/docker/litellm`.

AC-2. With deploy enabled, the script updates both local NAS and Fedora stack `.env` `LITELLM_IMAGE` values to the built image.

AC-3. The Fedora deploy pulls and recreates only the `litellm` service using the remote stack compose file and env file.

AC-4. Fedora deploy can be disabled by CLI flag or environment variable.

AC-5. Build-only mode still skips all deploy actions.

AC-6. Verification covers shell syntax and command-path review; live release run provides final deploy evidence.
