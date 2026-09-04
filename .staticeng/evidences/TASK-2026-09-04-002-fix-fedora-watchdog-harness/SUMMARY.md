# TASK-2026-09-04-002 Reopen 3 Evidence

## Summary

PASS pending renewed Tech Lead review. Reopen 3 makes the kernel journal OOM probe distinguish clean no-match from every timeout, permission, and pipeline error; errors now invalidate the sample. It also proves generated-collector command timeout/error behavior and preserves one-second lost-sample cycle timing

The collector emits one atomic 43-field allowlisted row or fails the sample. Every external collector command has a hard timeout, the whole collector has a separate hard timeout, and a hang counts as a lost sample. The watchdog permits at most two consecutive lost samples before exact rollback. Candidate baseline `B` remains the maximum of the final 30 healthy pre-request one-second samples

## Work Performed

- Changed kernel journal collection to require a successful bounded `journalctl`, then classify grep status 0 as match, 1 as clean no-match, and every other status as failure
- Added direct generated-collector timeout/error tests for Docker, PostgreSQL, Redis, health, dependency, and journal commands, plus journal match/no-match differentiation
- Applied `sleep=max(0, 1-elapsed)` to lost and healthy cycles; three 0.75-second sample timeouts roll back after 2.810 seconds in the behavioral proof
- Required protected baseline, control state, future maintenance deadline, rollback-confidence state, dependency baseline, and watchdog start time before arming; missing or invalid prerequisites invoke rollback
- Added independent enforcement of candidate manifest `sha256:b4c960...`, config `sha256:ad33017...`, and source `bf58974...`
- Changed signal handling to terminate and wait for the diagnostic client before invoking rollback, including while the collector is hung
- Retained all prior TASK-007 absolute, delta, monotonic growth, host, resource, health, identity, OOM, protected-state, deadline, and rollback gates
- Retained a sanitized Reopen 2 transcript and every 43-field allowlisted row from a non-mutating Fedora proof

## Acceptance Criteria Coverage

- **AC-1: PASS.** Valid fail-closed syntax, final-30 maximum `B`, every TASK-007 threshold, and exact rollback remain unchanged. Candidate manifest/config/source identities are enforced independently
- **AC-2: PASS.** Maintained scripts and generated `rollback.sh`, collector, and watchdog pass `bash -n`; generation fails if any emitted shell is invalid
- **AC-3: PASS.** Existing Fedora proof remains valid: 31 healthy rollback-image samples, 29.08 seconds first through thirtieth, live after row 30, 43 fields per row, and identical before/after state. Reopen 3 required and performed no new Fedora action. See `logs/03-reopen2-fedora-sanitized-proof.log`
- **AC-4: PASS.** Generated-collector Docker/PostgreSQL/Redis/health/dependency/journal timeout and error tests pass; journal match and no-match remain distinct; three whole-sample timeouts reach rollback in 2.810 seconds. The complete prior matrix remains green. See `logs/01-local-syntax-and-behavior.log`
- **AC-5: PENDING.** Reopen 3 is ready for renewed Tech Lead review. No commit or push was made

## Documentation Impact

No product or architecture documentation update is required. This correction restores the existing TASK-007 operational contract and changes no steady-state product or runtime behavior

## Open Risks

- The candidate remains blocked until renewed Tech Lead PASS and PMA authorization
- The Fedora proof intentionally exercised only read-only collection against the healthy rollback image. Candidate execution remains outside this task

## Recommended Next Step

Tech Lead should review the hard timeout boundaries, prerequisite gates, independent identities, client-before-rollback ordering, complete behavioral matrix, retained 31-row Fedora evidence, and exact rollback controller

## Tech Lead Reopen 2 Review

REJECT. Bounded review passes prerequisite existence and validity gates, exact candidate manifest/config/source checks, final-30 maximum baseline behavior, thresholds and monotonic paths, real HUP/INT/TERM behavior, diagnostic-client termination before rollback, exact rollback identity/command, and the retained Fedora proof. Independent parsing confirms 31 rows, 43 fields, 30.08 seconds first-to-last, and 0.96 to 1.05-second adjacent cadence

Kernel OOM collection remains fail-open: a timeout or error from the `journalctl | grep` pipeline inside its `if` emits `kernel_oom=0` instead of failing the sample. The suite mocks whole-sample hangs but does not exercise command-level hangs in the generated collector. Lost timeout samples also add a full sleep after the 0.75-second sample deadline, delaying the third-miss rollback to about 4.25 seconds rather than three one-second cycles. AC-1, AC-4, and AC-5 fail; AC-2 and AC-3 pass. TASK-006 Reopen 7 remains unauthorized

## Tech Lead Reopen 3 Review

PASS. Independent bounded verification confirms kernel journal match/no-match/error separation, generated command-level timeout/error behavior, 2.796-second rollback across three 0.75-second lost samples, exact identity and prerequisite gates, all prior signal/threshold/monotonic behavior, diagnostic-client termination before rollback, and the exact rollback controller

Maintained and generated Bash syntax, ShellCheck, full behavioral tests, diff whitespace, and StaticEng validation pass. The retained non-mutating Fedora proof independently parses as 31 rows with 43 fields each, 30.08 seconds first-to-last, and 0.96 to 1.05-second adjacent cadence with identical before/after rollback state. AC-1 through AC-5 pass. No product or architecture documentation is required; non-runtime hardening remains deferred under TASK-023
