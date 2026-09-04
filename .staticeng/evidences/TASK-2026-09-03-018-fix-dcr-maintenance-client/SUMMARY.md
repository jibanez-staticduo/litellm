# TASK-2026-09-03-018 Evidence Summary

## Outcome

BLOCKED/DEFERRED experimental source checkpoint. Bounded source review, secret scan, and 143 maintenance/runner/shared tests pass. The single TASK-022 run remains a functional failure: it did not prove full DCR/exact audience and automatic cleanup retained one exact owned volume. Tech Lead removed only that verified volume and confirmed zero task resources plus unchanged healthy NAS production. The harness is retained for maintenance development without functional approval or retry authorization

## Acceptance Criteria

- **AC-1: PASS.** `tests/e2e/maintenance/dcr_maintenance_client.py` owns one `httpx.Client` from login through register, authorize, complete, token, and audience checks. Focused tests prove cookies exist during the flow and are cleared at teardown
- **AC-2: PASS.** Returned client-secret presence is rejected before typed response validation, so its value cannot enter an exception. Secret/cookie values have no file, output, environment, or command-argument path
- **AC-3: FAIL.** Source identity checks pass, but the concrete run did not produce full DCR or exact-audience success evidence
- **AC-4: FAIL.** Automatic cleanup retained one owned PostgreSQL volume; exact Tech Lead cleanup restored zero resources. Production and Fedora remained untouched
- **AC-5: PASS FOR SOURCE CHECKPOINT ONLY.** Tech Lead accepts the maintained harness for commit as blocked/experimental. This is not functional approval and does not authorize another disposable run

## Verification

See `logs/27-reopen13-verification.log` and `logs/28-tech-lead-reopen13-execution.log`. Canonical review and 143 tests pass; the one authorized concrete run and automatic cleanup failed. Final checkpoint verification reconfirmed the same test/static result, no credential signatures, zero task resources, and invariant production

Source checkpoint commit: `43e437c100` (`test: TASK-2026-09-03-018 checkpoint DCR maintenance harness`). Functional qualification remains blocked/deferred

## Boundaries

Only test harness, disposable synthetic candidate config, test policy, CodeMap, task, and evidence files changed. No retained candidate container was started. The concrete inspector binds the actual named disposable container's running image ID and mounted config digest before any HTTP session opens
