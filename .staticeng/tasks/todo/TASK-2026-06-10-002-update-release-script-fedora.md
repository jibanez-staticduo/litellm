---
task_id: TASK-2026-06-10-002-update-release-script-fedora
complexity: standard
track: implementation
slice: core
status: completed
assigned_to: developer
handoff_from: product_manager
scr: SCR-2026-06-10-002-release-script-fedora-deploy
parent: none
discussion: DISCUSSION-002
external_file: /home/staticduo/git/release-litellm.sh
---

# Update LiteLLM Release Script For Fedora Deploy

## Classification

- complexity: standard
- track: implementation
- slice: core

## Context

The user asked to run the LiteLLM release/update script and also modify it so future releases update the Fedora LiteLLM deployment in addition to the NAS deployment. The script is outside the LiteLLM repo at `/home/staticduo/git/release-litellm.sh`.

Current script behavior:
- Production workdir default: `/home/staticduo/git/litellm-production-main`
- Local stack dir default: `/volume2/docker/litellm`
- Builds and pushes `docker.staticduo.com/litellm:<tag>` and stable tag.
- If deploy enabled, updates local stack `.env` and recreates local `litellm` service.

Fedora stack:
- SSH host: `fedora`
- Stack dir: `/home/staticduo/docker/litellm`

## Acceptance Criteria

AC-1. `release-litellm.sh` has configurable Fedora host and stack directory defaults: `fedora` and `/home/staticduo/docker/litellm`.

AC-2. With deploy enabled, the script updates both local NAS and Fedora stack `.env` `LITELLM_IMAGE` values to the built image.

AC-3. The Fedora deploy pulls and recreates only the `litellm` service using the remote stack compose file and env file.

AC-4. Fedora deploy can be disabled by CLI flag or environment variable.

AC-5. Build-only mode still skips all deploy actions.

AC-6. Verification covers shell syntax and command-path review; live release run provides final deploy evidence.

## Expected Evidence

Create `.staticeng/evidences/TASK-2026-06-10-002-update-release-script-fedora/` with `SUMMARY.md` and logs for syntax/checks. If the PMA run produces live release logs later, include them or note that PMA owns live release evidence.

## Handoff

[Agent Message] From: product_manager To: developer
Please update `/home/staticduo/git/release-litellm.sh` only. Keep the change minimal and robust with SSH quoting. Do not run the full release script. Verify with shell syntax checks and any safe dry command review available. Return Summary, Work Performed, Acceptance Criteria Coverage, Documentation Impact, Open Risks, Recommended Next Step.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

- Updated `/home/staticduo/git/release-litellm.sh` only for release logic.
- Added Fedora deploy defaults: `FEDORA_HOST=fedora`, `FEDORA_STACK_DIR=/home/staticduo/docker/litellm`, `FEDORA_DEPLOY=1`.
- Added `--no-fedora-deploy` and `FEDORA_DEPLOY=0` opt-out support.
- Preserved existing local NAS deploy and added a deploy-enabled remote Fedora path that updates `.env`, pulls `litellm`, and runs `docker compose up -d litellm` using the remote compose file and env file.
- Verified with `bash -n` and safe command-path review; evidence is in `.staticeng/evidences/TASK-2026-06-10-002-update-release-script-fedora/`.
- Full release script was not run per handoff.
