---
id: TASK-2026-07-08-001-deploy-empty-output-fix-fedora
complexity: standard
track: implementation
slice: foundation
status: done
scr: null
parent: null
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-07-08-001 - Deploy Empty Output Fix to Fedora

## Classification
- **complexity:** standard
- **track:** implementation
- **slice:** foundation

## Objective
Deploy the current LiteLLM image containing the ChatGPT account2 empty-output fix to the Fedora LiteLLM stack without losing or mutating any existing Fedora model definitions.

## Scope
- Deploy Fedora only; local/NAS is already running the fixed image.
- Target image: `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-chatgptprofiles-emptyoutputfix-20260708`.
- Source commit for image: `fe302bf88d1864570b0aeb24d45951aee2a2e225`.
- Capture Fedora current image/rollback reference before changing anything.
- Capture Fedora model inventory before and after deploy, compare counts/names/deployment ids where available, and prove no model loss.
- Verify Fedora container health/readiness/liveliness after deploy.
- Run safe smoke tests for representative existing Fedora models if feasible, and at minimum verify `/model/info` is intact.
- Do not add, delete, or update Fedora models.
- Do not expose `.env`, master keys, API keys, tokens, cookies, auth files, refresh tokens, private keys, session tokens, DB URLs, or auth headers.

## Pre-existing Worktree State
- Before task creation, the worktree had only `.staticeng` changes: generated PMA file drift and evidence path normalization in prior task summaries.
- No application code changes were dirty.
- PMA secret scan found no high-confidence secrets in dirty files.

## Acceptance Criteria
- [x] AC-1: Fedora previous image and rollback reference are captured.
- [x] AC-2: Fedora model inventory is captured before deployment using secret-safe output.
- [x] AC-3: Fedora LiteLLM is running the target fixed image after deployment.
- [x] AC-4: Fedora health checks pass after deployment.
- [x] AC-5: Fedora post-deploy model inventory matches the pre-deploy inventory for existing models; no model names/deployments are lost.
- [x] AC-6: At least one safe Fedora model smoke or equivalent admin/API validation succeeds after deployment.
- [x] AC-7: Evidence packet exists under `.staticeng/evidences/TASK-2026-07-08-001-deploy-empty-output-fix-fedora/` with `SUMMARY.md` and safe logs.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-07-08-001-deploy-empty-output-fix-fedora/` containing:
- `SUMMARY.md` mapping AC-1 through AC-7.
- `logs/` with safe preflight, model inventory comparison, deployment, health, and smoke outputs.
- No secret values.

## Handoff
[Agent Message] From: product_manager To: developer

Please deploy the fixed LiteLLM image to Fedora without losing any model definitions. Start with read-only preflight and model inventory. Capture rollback. Deploy only the image, do not mutate models. After deployment, compare the post-deploy model inventory with the pre-deploy inventory and prove no models were lost. Keep all evidence secret-safe. Do not commit; PMA owns closure.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

### Summary
- Deployed Fedora LiteLLM to `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-chatgptprofiles-emptyoutputfix-20260708`.
- Target digest: `docker.staticduo.com/litellm@sha256:1c83fa329b7c3e5d4e04ccd03da9a345c373d24123b6a0b060de4d178f6c1316`.
- Only Fedora `/home/staticduo/docker/litellm/.env` `LITELLM_IMAGE` was changed.
- No Fedora model definitions were added, removed, or edited.

### Verification
- Previous image captured: `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-cachecodecfix-20260707`.
- Rollback digest captured: `docker.staticduo.com/litellm@sha256:23f346521079a27dfeb9039e73dc2328c268ec50d44e11dc662c33d78a006d86`.
- Docker container status `running`, health `healthy`.
- `/health/liveliness` and `/health/readiness` returned HTTP 200.
- Pre/post model inventories matched exactly: 9 deployments, same model names, same deployment IDs.
- Admin/API validation succeeded: `/model/info` and `/v1/models` returned HTTP 200 with 9 entries.

## PMA Final Closure

### Acceptance Criteria Coverage
- AC-1 through AC-7 are satisfied by the evidence summary and logs.
- PMA rechecked Fedora container image/status/health directly after the handoff.

### Documentation Impact
- Evidence-only operational release documentation.

### Open Risks
- No provider completion smoke was run on Fedora to avoid external/private model traffic; admin/model-info validation proved model preservation and service health.
- `staticeng_validate` remains known non-green due unrelated baseline CodeMap/link debt.
