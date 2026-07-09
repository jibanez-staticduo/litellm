---
id: TASK-2026-07-08-001-deploy-empty-output-fix-fedora
complexity: standard
track: implementation
slice: foundation
status: todo
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
- [ ] AC-1: Fedora previous image and rollback reference are captured.
- [ ] AC-2: Fedora model inventory is captured before deployment using secret-safe output.
- [ ] AC-3: Fedora LiteLLM is running the target fixed image after deployment.
- [ ] AC-4: Fedora health checks pass after deployment.
- [ ] AC-5: Fedora post-deploy model inventory matches the pre-deploy inventory for existing models; no model names/deployments are lost.
- [ ] AC-6: At least one safe Fedora model smoke or equivalent admin/API validation succeeds after deployment.
- [ ] AC-7: Evidence packet exists under `.staticeng/evidences/TASK-2026-07-08-001-deploy-empty-output-fix-fedora/` with `SUMMARY.md` and safe logs.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-07-08-001-deploy-empty-output-fix-fedora/` containing:
- `SUMMARY.md` mapping AC-1 through AC-7.
- `logs/` with safe preflight, model inventory comparison, deployment, health, and smoke outputs.
- No secret values.

## Handoff
[Agent Message] From: product_manager To: developer

Please deploy the fixed LiteLLM image to Fedora without losing any model definitions. Start with read-only preflight and model inventory. Capture rollback. Deploy only the image, do not mutate models. After deployment, compare the post-deploy model inventory with the pre-deploy inventory and prove no models were lost. Keep all evidence secret-safe. Do not commit; PMA owns closure.
