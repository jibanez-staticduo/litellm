---
id: TASK-2026-07-11-003-release-multiaccount-routing-fix-both
complexity: standard
track: implementation
slice: foundation
status: done
scr: null
parent: TASK-2026-07-11-002-fix-multiaccount-routing-oauth
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-07-11-003 - Release Multiaccount Routing Fix to Both LiteLLM Instances

## Classification
- **complexity:** standard
- **track:** implementation
- **slice:** foundation

## Objective
Build a durable LiteLLM image from commit `8dcccc5cd2` and deploy it to local/NAS and Fedora without losing model definitions or credentials, then validate regular/account2 routing isolation and service health.

## Scope
- Capture current images/digests and rollback references for both instances.
- Capture pre-deploy model inventories and sanitized auth-profile presence state; do not read/log credential contents.
- Build/push one new image from current `main`.
- Deploy local/NAS and Fedora.
- Verify health/readiness/liveliness and exact model inventory preservation.
- Run safe routing smokes for regular `chatgpt/gpt-5.6-sol`; do not trigger Fedora account2 auth.
- On local/NAS, account2 is authenticated and may receive a minimal safe account2 smoke.
- Capture structured routing logs proving selected profile/deployment without secrets.

## Acceptance Criteria
- [x] AC-1: New image is built from `8dcccc5cd2` or later and pushed with digest.
- [x] AC-2: Local/NAS runs new image healthy; model inventory preserved.
- [x] AC-3: Fedora runs new image healthy; model inventory preserved.
- [x] AC-4: Regular Sol requests select default profile only on both instances.
- [x] AC-5: Local account2 Sol selects account2 only.
- [x] AC-6: Fedora account2 auth is not triggered.
- [x] AC-7: Rollback references captured for both instances.
- [x] AC-8: Evidence packet exists under `.staticeng/evidences/TASK-2026-07-11-003-release-multiaccount-routing-fix-both/` with `SUMMARY.md` and safe logs.

## Handoff
[Agent Message] From: product_manager To: developer

Build and deploy the committed multiaccount routing/OAuth fix to both LiteLLM instances. Preserve all model rows and auth files. Capture rollback and pre/post inventories. Validate regular routing on both and account2 routing only on local/NAS; do not trigger Fedora account2 device auth. Capture sanitized structured routing evidence. Do not commit.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

### Summary
- Built and pushed `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-multiaccount-routingfix-20260711` from commit `8dcccc5cd201d777aee23e3004242e73d8ed4207`.
- Digest: `sha256:ca28db906704c63afc9b73bd40a201edadb10da30e214542fcada54748dd2497`.
- Deployed successfully to local/NAS and Fedora.
- Stopped only `/volume2/docker/updatedockers` during local deployment, then restarted it healthy; local LiteLLM remained on target image.

### Verification
- Local/NAS and Fedora containers are running/healthy; readiness and liveliness HTTP 200.
- Exact inventories preserved: local 26, Fedora 19.
- Local regular Sol: HTTP 200, default profile, deployment `11dbce7b` prefix.
- Local account2 Sol: HTTP 200, account2 profile, deployment `59183bd1` prefix.
- Fedora regular Sol: HTTP 200, default profile, deployment `9007ab1c` prefix.
- Fedora account2 was not called; no device auth was triggered.

### Rollback
- Local: `docker.staticduo.com/litellm:rollback-multiaccount-routingfix-local-20260711`.
- Fedora: `docker.staticduo.com/litellm:rollback-multiaccount-routingfix-fedora-20260711`.

## PMA Final Closure

### Acceptance Criteria Coverage
- AC-1 through AC-8 satisfied by evidence and PMA direct container status verification.

### Documentation Impact
- Evidence-only operational release documentation.

### Open Risks
- Existing auth files retain prior broad modes; no credential content or mode was changed during release.
- StaticEng validation remains non-green due unrelated CodeMap debt.
