# TASK-2026-09-03-017 Evidence Summary

## Summary

PASS and closed after Tech Lead Reopen 2 review. The disposable runtime's documented authorization-cache TTL is 60 seconds. The lifecycle regression distinguishes handler-level 404 from authentication denial, preserves authoritative key/database absence, and polls a harmless retained-key request until true 401 denial at 60.50 seconds. Runtime authentication source is unchanged

## Acceptance Criteria Coverage

- **AC-1: PASS.** No runtime source, authentication lookup, schema, migration, image, service, Fedora, or NAS behavior changed. The harness uses the existing email-only database login boundary
- **AC-2: PASS.** Before deletion, the retained key exists and receives the expected viewer 403. After deletion, master-authenticated `/key/info` returns 404 and direct database checks return zero task user/key rows. Retained-key `/user/info` 404 is recorded as handler-level proof that cached admission still succeeds. A separate harmless retained-key `/user/list` poll then reaches true authentication 401 at 60.50 seconds, within the 60-second TTL plus 10-second bound
- **AC-3: PASS.** Reopen 2's focused live disposable-PostgreSQL regression, 139 mapped auth/login/management tests, 27 e2e harness tests, coverage registry, e2e raw-HTTP gate, Ruff, basedpyright, and `staticeng_validate` pass
- **AC-4: PASS.** Tech Lead approved closure and owns the non-force push. No runtime source change requires image rebuild/signing, and no publication, deployment, Fedora access, or NAS access occurred

## Verification

- `logs/01-live-disposable-lifecycle.log`
- `logs/02-source-and-static-gates.log`
- `logs/03-cleanup.log`
- `logs/05-reopen1-verification.log`
- `logs/06-tech-lead-reopen1-review.log`
- `logs/07-reopen2-cache-expiry-verification.log`
- `logs/08-tech-lead-reopen2-review.log`

## Documentation Impact

The approved SCR and blocked maintenance task now explicitly require distinct generated `user_id` and `user_email` values, email in `/login` form field `username`, and returned ID for management and cleanup. No product or architecture document and no CodeMap change is required because runtime behavior and navigable source are unchanged

## Open Risks

The regression uses the existing shared live-e2e harness and therefore requires a migrated disposable database plus a live proxy. It does not broaden database authentication to accept user IDs. Revocation is bounded but not immediate: the disposable no-Redis runtime continues admitting the cached key until the configured/default 60-second in-memory TTL expires

## Recommended Next Step

Tech Lead should review the focused harness and contract changes, rerun the listed gates if needed, then own commit and push. PMA may reopen TASK-006 only after that review and must preserve every existing maintenance, cleanup, one-request, rollback, and host-exclusion boundary

## Signed Handoff

[Agent Message] From: developer To: product_manager

TASK-017 PASS FOR TECH LEAD REVIEW. Added and ran the disposable database lifecycle regression: distinct generated email and opaque ID, `/user/new`, password-only update by returned ID, ID and wrong-password rejection, email login success, least-privilege read-back, deletion, zero task users/keys, and post-delete rejection all pass. The SCR and TASK-006 now require email-only login while retaining ID for management and cleanup. Runtime auth source is unchanged. All focused auth/proxy/source/static gates pass, disposable resources are removed, and no rebuild, commit, push, deployment, Fedora, or NAS action occurred

## Tech Lead Review

REJECT. Fresh mapped review gates pass and no runtime source changed, but AC-2 remains open. The automated lifecycle test does not assert that the generated UI session key is absent or rejected after `/user/delete`, so an orphan-key regression would pass. It also verifies viewer metadata and JWT claims without exercising a denial that proves the minted session enforces least privilege. See `logs/04-tech-lead-review.log`

[Agent Message] From: tech_lead To: product_manager

TASK-017 REJECTED. Add mutation-sensitive generated-session-key cleanup and enforced least-privilege denial coverage, then return the same task for rereview. No close, commit, or push occurred

## Reopen 1 Developer Result

PASS. The retained session key is proven present before deletion, is denied 403 on the proxy-admin-only `/user/list` route while its own `/user/info` remains permitted, then is absent from `/key/info` with 404 after `/user/delete`. The same key can no longer resolve the deleted user, and direct final disposable-DB checks prove zero matching users and keys. See `logs/05-reopen1-verification.log`

[Agent Message] From: developer To: product_manager

TASK-017 REOPEN 1 PASS FOR TECH LEAD REREVIEW. The regression now enforces viewer denial with the retained UI session key, proves that exact key exists before deletion, and proves it is absent and cannot resolve its user after `/user/delete`, with zero task user/key rows and restored baseline. The live lifecycle and all mapped auth/harness/lint/type/static gates pass. Runtime auth remains unchanged; no commit, push, build, deploy, Fedora, or NAS action occurred

## Tech Lead Reopen 1 Review

REJECT. The retained session key exists and is denied the proxy-admin-only operation before deletion. Master-authenticated `/key/info` 404 and direct database checks prove storage cleanup. However, retained-key `/user/info` returning 404 proves that the deleted key still passed bearer authentication and self-access authorization before the handler found the user absent. This is not an invalid/unauthorized admission result and does not prove exact-key unusability. See `logs/06-tech-lead-reopen1-review.log`

[Agent Message] From: tech_lead To: product_manager

TASK-017 REOPEN 1 REJECTED. Require an authentication denial for the exact retained key after cache expiry, in addition to database absence and baseline restoration. No close, commit, or push occurred

## Reopen 2 Developer Result

PASS. Source documents a 60-second default `UserAPIKeyCacheTTLEnum.in_memory_cache_ttl`, configurable by `general_settings.user_api_key_cache_ttl`, with `_cache_key_object` using `get_management_object_ttl`. In the exact disposable no-Redis config, no override exists, so the effective TTL is 60 seconds. After deletion, `/key/info` 404 and zero rows establish authoritative absence; retained-key `/user/info` 404 is correctly treated as handler-level cached admission. Harmless retained-key `/user/list` remained 403 only during that cache window and returned true authentication 401 after 60.50 seconds. See `logs/07-reopen2-cache-expiry-verification.log`

[Agent Message] From: developer To: product_manager

TASK-017 REOPEN 2 PASS FOR TECH LEAD REREVIEW. The disposable runtime auth-cache TTL is documented and effective at 60 seconds. Exact key/database absence remains proven immediately after delete; handler 404 is correctly classified as cached admission; and a harmless retained-key request reaches true 401 denial after 60.50 seconds within the TTL plus 10-second bound. All requested gates pass, runtime auth is unchanged, and no prohibited action occurred

## Tech Lead Reopen 2 Review

PASS. Source and exact runtime evidence establish a 60-second effective no-Redis authorization-cache TTL. The regression proves immediate user/key storage deletion, correctly classifies retained-key `/user/info` 404 as cached admission, and requires true `/user/list` authentication 401 within 70 seconds. Viewer denial, email-versus-ID behavior, baseline restoration, raw-HTTP confinement, and every mapped gate pass. Maintenance compatibility is conditional on its already mandatory supported deletion of the separately addressable UI key and immediate destruction of client-held auth artifacts; this cache-expiry check is fallback qualification, not an operational delay or reuse allowance. See `logs/08-tech-lead-reopen2-review.log`

[Agent Message] From: tech_lead To: product_manager

TASK-017 REOPEN 2 PASS AND CLOSED. The exact lifecycle and all mapped gates pass with no runtime source, image, deployment, Fedora, or NAS change
