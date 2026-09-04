# Current Tasks (Backlog)

## Active Discussions
- (None)

## Active
- TASK-2026-08-28-009-define-resilient-lazymcp-discovery
- TASK-2026-09-01-001-qualify-lazymcp-oauth-release
- TASK-2026-09-01-002-design-dual-host-release
- TASK-2026-09-01-005-review-release-qualification
- TASK-2026-09-01-007-spec-upstream-main-integration
- TASK-2026-09-01-008-design-upstream-main-integration
- TASK-2026-09-01-011-qualify-upstream-isolated-candidate
- TASK-2026-09-03-002-review-fedora-release-readiness
- TASK-2026-09-03-003-verify-fedora-schema-upgrade-rollback
- TASK-2026-09-03-004-sign-attest-release-images
- TASK-2026-09-03-005-spec-fedora-maintenance-investigation
- TASK-2026-09-03-006-diagnose-fedora-candidate-live
- TASK-2026-09-03-016-investigate-internal-user-login

## Todo
- TASK-2026-07-14-003-trigger-nas-account2-reauth
- TASK-2026-08-26-003-remove-unused-litellm-reasoning-policy
- TASK-2026-08-26-004-implement-client-qwen38-modes

## Blocked
- TASK-2026-09-03-008-prepare-fedora-dcr-credential — healthy rollback image lacks exact toolset DCR discovery and transport routes; no bearer could be minted or audience-tested
- TASK-2026-09-01-012-release-upstream-main-fedora — exact candidate rolled back after authorized real-tool timeout and unhealthy transition; investigation and fresh reauthorization required
- TASK-2026-09-01-003-deploy-lazymcp-oauth-fedora — promotion qualification failed; Tech Lead explicitly rejected deployment
- TASK-2026-09-01-004-deploy-lazymcp-oauth-nas — blocked by failed qualification and unauthorized Fedora canary
- TASK-2026-08-15-002-expand-npm-litellm-response-buffers — technical work complete; blocked only by pre-existing repository-wide StaticEng CodeMap validation debt
- TASK-2026-08-25-007-build-stage-deepseek-policy-image — candidate built and rolled back; staging health blocked by pre-existing ChatGPT reauthentication
- TASK-2026-08-25-009-run-isolated-deepseek-verification — isolated clone cannot load the three retained encrypted model records without a decided encryption-context strategy
- TASK-2026-08-25-014-publish-opencode-litellm-019 — npm authentication returns E401; no release mutation occurred
- TASK-2026-08-25-016-activate-local-opencode-deepseek-variants — real UI shows generic Medium/default and invalid literal off wire value; plugin correction required
