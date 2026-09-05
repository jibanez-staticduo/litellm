# TASK-2026-09-04-005 Evidence Summary

## Reopen 3: Collector Projections

Tech Lead final verdict: PASS. Independently reran both full suites and ShellCheck; generated Bash syntax and StaticEng validation pass with zero warnings. Reviewed every inspection site including generated child collector and dependency loop: only fixed scalar projections are retrieved. The 43-field sample output and seven-field dependency TSV fingerprint order remain unchanged. AC-1 through AC-5 pass. Executor may immediately continue the existing authorized TASK-006 diagnosis after closure push; this review performs no deployment. Fourteen unrelated normalization files remain preserved outside the commit. See `.staticeng/evidences/TASK-2026-09-04-005-fix-deployment-controller/logs/09-tech-lead-reopen3-review.md`

Replaced broad Docker reads only in the generated collector with fixed JSON arrays of scalar fields. Container projection: configured image, runtime image, ID, start time, PID, exit code, restart count, OOM flag, health. Image projection: ID and exact `org.opencontainers.image.revision` label. Dependency projection: ID, image, start time, status, health, restart count, OOM flag, in the prior TSV fingerprint order. No environment, whole Config, or whole inspect object is retrieved

Controller, rollback, thresholds, and 43-field sample contract remain unchanged. Exact-command mocks and successful projection tests plus both full regression suites pass; ShellCheck and diff checks pass. See `logs/08-reopen3-projections.log`. Independent approval pending; no deployment, credentials, commit, or push

## Final Tech Lead Reopen 2 Verdict

PASS. Independent full controller/watchdog suites, maintained/generated Bash syntax, ShellCheck, whitespace, and StaticEng validation pass. Previous startup OOM coverage, nonce/lock readiness and rollback intent, pre-mutation signal/rollback-failure preservation, and runtime config identity findings are closed. AC-1 through AC-5 pass under PMA's review-only closure and original-session execution handoff

See `.staticeng/evidences/TASK-2026-09-04-005-fix-deployment-controller/logs/08-tech-lead-reopen2-review.md`. Historical rejected reviews below are superseded. No live deployment or credential/request use occurred. Original execution session is authorized to resume the existing TASK-006 direct-admin diagnosis after closure push, with all fresh preflight, OOM, exact rollback, one-request, full Fedora gates, and soak controls retained. NAS follows only fully successful Fedora and separate PMA activation. Unrelated StaticEng path normalizations remain preserved outside this closure commit

## Current Outcome: Reopen 2

Ready for independent review, not deployment approval. Earlier Reopen 1 PASS claims below are historical and superseded by the Tech Lead rejection and this correction

Pre-start now observes the appearing container's cgroup memory/growth/OOM/restart/process gates with startup-tolerant health. Frozen nonce ownership serializes ready publication, controller acceptance, selector replacement, and rollback. Rollback intent precedes lock acquisition. The prior selector is an exclusive immutable snapshot validated against the frozen rollback reference; rollback never installs candidate bytes

AC-1 through AC-4 verification: `logs/05-reopen2-validation.log` retains both full suites, including startup absolute/rate/OOM/restart/PID/FD/exit gates, initial OOM detection, health tolerance, generated watcher nonce success/rejection, rollback-intent precedence, final-boundary rollback after ready, and pre-selector signal with rollback failing before restore. Maintained/generated Bash syntax, ShellCheck, diff check, and StaticEng validation pass. AC-5 remains pending Tech Lead review

Unrelated StaticEng normalizations are preserved. No deploy, credential use, diagnostic request, commit, or push. NAS promotion remains conditional on successful Fedora qualification and is outside this implementation

## Summary

Implemented the complete Fedora candidate startup controller as one governed shell file. The controller validates itself plus the approved watcher, rollback, and collector before atomically changing the selector. It uses the SCR allowlisted container projection, fails closed on every startup branch, invokes the approved rollback after any post-selector failure, and does not load credentials or issue the diagnostic request

## Verification

- **AC-1: PASS.** `fedora-maintenance-controller.sh` contains the complete selector, recreate, bounded startup, real-watcher arm, and rollback control. The complete controller and isolated test pass `bash -n` and ShellCheck with no findings
- **AC-2: PASS.** Compound command fallbacks use valid spaced syntax or explicit `if` branches. Error, signal, startup, watcher-start, and exit paths fail closed, and rollback failure is surfaced as status 70
- **AC-3: PASS.** The isolated startup-health failure test mutates only a temporary fixture, arms then terminates the mock watcher, invokes rollback exactly once, restores the rollback selector, leaves the credential fixture byte-identical, and creates no request marker
- **AC-4: PASS.** The controller requires and validates its complete file, approved watcher, approved rollback, collector, prerequisites, and exact rollback wiring before selector replacement. The test's Docker stub rejects selector mutation unless the validation marker already exists
- **AC-5: PENDING.** Tech Lead review, commit, and TASK-006 Reopen 9 execution remain outside Developer authority

## Scope And Safety

No Fedora or NAS access occurred. No production selector, credential, request, service, container, database, host configuration, or LiteLLM runtime source was read or mutated. The only execution used isolated temporary fixtures and command stubs

## Artifacts

- Controller: `.staticeng/evidences/TASK-2026-09-04-005-fix-deployment-controller/harness/fedora-maintenance-controller.sh`
- Isolated test: `.staticeng/evidences/TASK-2026-09-04-005-fix-deployment-controller/harness/test-fedora-maintenance-controller.sh`
- Syntax and startup-failure evidence: `.staticeng/evidences/TASK-2026-09-04-005-fix-deployment-controller/logs/01-bash-syntax-and-startup-failure.log`
- ShellCheck evidence: `.staticeng/evidences/TASK-2026-09-04-005-fix-deployment-controller/logs/02-shellcheck.log`
- Diff check evidence: `.staticeng/evidences/TASK-2026-09-04-005-fix-deployment-controller/logs/03-diff-check.log`
- StaticEng validation evidence: `.staticeng/evidences/TASK-2026-09-04-005-fix-deployment-controller/logs/04-staticeng-validate.log`

## Documentation Impact

No product, architecture, technical, or CodeMap update is required. This is a governed one-off maintenance controller correction and does not change steady-state product/runtime behavior or navigable maintained source

## Open Risks

The controller intentionally stops after arming the real watcher and completing bounded candidate startup. The already governed diagnostic client, full gates, and soak remain TASK-006 responsibilities. Tech Lead must review the exact host attempt wiring before execution

## Reopen 1

The watcher/controller now use explicit `pre-start`, `active`, and ready acknowledgements. Pre-start preserves host, dependency, protected-state, deadline, rollback-confidence, and kernel-OOM controls while deferring only candidate identity/health checks until exact startup passes. The controller atomically arms rollback-required before selector replacement and requires watcher-owned active exact-state readiness before handoff

Isolated normal startup, startup failure, final-check race, and signal-between-state-and-selector tests pass. The full prior watchdog threshold, signal, timeout, failure, exact rollback, and proof-isolation matrix also remains green. No Fedora/NAS access or mutation, credentials, requests, service action, or runtime-source change occurred

## Tech Lead Review 1

REJECT. Independent `bash -n`, ShellCheck, the isolated startup-failure test, diff whitespace, and StaticEng validation pass. Functional and rollback-control review found three blockers

- The unchanged watcher immediately rolls back on non-healthy or non-200 startup samples, so launching it before the bounded startup poll can reject a normally starting candidate before the poll allowance can operate
- The controller does not recheck watcher liveness or rollback state after its final inspect/health sequence, so it can publish readiness after the watcher has tripped during those checks
- The controller arms `mutation_started` after selector replacement, leaving a trapped-signal interval in which the changed selector is not rolled back

AC-1 through AC-3 pass, AC-4 is partial on behavioral compatibility, and AC-5 fails. No commit, push, deployment, credential use, or request occurred. TASK-006 Reopen 9 is not authorized

## Tech Lead Reopen 1 Review

REJECT. Independent full controller and watcher behavioral suites, Bash syntax, ShellCheck, diff whitespace, and StaticEng validation pass, but three functional/OOM/rollback blockers remain

- `pre-start` spans candidate recreation and the full startup poll, while candidate cgroup memory, growth, OOM-event, restart, and process limits run only in `active`. Candidate startup therefore lacks the mandatory absolute and delta OOM gates
- Final readiness uses separate file reads without shared serialization with watcher `trip`. A trip can begin after the controller's last trigger check, or remove ready/active state before publishing its trigger, while the controller proceeds to successful handoff
- A signal before selector replacement makes rollback move the prepared candidate selector into place first. A rollback failure can therefore leave the candidate selected even though forward replacement had not begun

The existing tests cover normal startup, startup timeout, a trip before ready publication, and successful pre-selector signal rollback. They do not close startup OOM, final handoff, or signal-plus-rollback-failure behavior. No commit, push, deployment, credential use, or request occurred. TASK-006 Reopen 9 remains unauthorized
