# TASK-2026-09-03-018 Evidence Summary

## Outcome

REJECT at Tech Lead Reopen 13 functional execution. Bounded canonical Docker Hub repository-plus-exact-digest review passes, including hostile cases and all exact config/platform/version checks. The single TASK-022 runner invocation returned status-only failure, did not prove full DCR/exact audience, and left one exact task-owned PostgreSQL volume. Tech Lead removed only that label/name-proven volume and confirmed zero task resources plus unchanged healthy NAS production

## Acceptance Criteria

- **AC-1: PASS.** `tests/e2e/maintenance/dcr_maintenance_client.py` owns one `httpx.Client` from login through register, authorize, complete, token, and audience checks. Focused tests prove cookies exist during the flow and are cleared at teardown
- **AC-2: PASS.** Returned client-secret presence is rejected before typed response validation, so its value cannot enter an exception. Secret/cookie values have no file, output, environment, or command-argument path
- **AC-3: FAIL.** Source identity checks pass, but the concrete run did not produce full DCR or exact-audience success evidence
- **AC-4: FAIL.** Automatic cleanup retained one owned PostgreSQL volume; exact Tech Lead cleanup restored zero resources. Production and Fedora remained untouched
- **AC-5: FAIL.** Tech Lead rejected closure, commit, push, and TASK-006/Fedora authorization

## Verification

See `logs/27-reopen13-verification.log` and `logs/28-tech-lead-reopen13-execution.log`. Canonical review and 143 tests pass; the one authorized concrete run and automatic cleanup failed

## Boundaries

Only test harness, disposable synthetic candidate config, test policy, CodeMap, task, and evidence files changed. No retained candidate container was started. The concrete inspector binds the actual named disposable container's running image ID and mounted config digest before any HTTP session opens
