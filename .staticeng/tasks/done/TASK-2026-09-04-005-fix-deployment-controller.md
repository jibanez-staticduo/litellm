---
id: TASK-2026-09-04-005-fix-deployment-controller
complexity: tiny
track: implementation
slice: qa
status: done
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-03-006-diagnose-fedora-candidate-live
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 3
---

# Task: Fix deployment controller

## Objective

Move the complete one-off Fedora maintenance controller into a governed script, correct all compound fallback syntax, and validate the whole controller before selector mutation.

## Acceptance Criteria

- [x] AC-1: Complete controller is one file and passes `bash -n` and ShellCheck.
- [x] AC-2: Every fallback uses valid fail-closed syntax.
- [x] AC-3: Startup-failure test proves rollback is invoked and no credential/request is consumed.
- [x] AC-4: Controller and real watcher are both validated before selector mutation.
- [x] AC-5: Tech Lead reviews, closes and commits the controller, and authorizes immediate TASK-006 Reopen 9 in the original execution session, without deploying during review (PMA Reopen 2 handoff).

## Handoff

[Agent Message] From: product_manager To: developer

Fix only the complete deployment controller script. Reuse the already approved watcher and rollback; do not redesign them. Put all logic in one file, run `bash -n`, ShellCheck, and one isolated startup-failure rollback test. No Fedora selector mutation or credential use. Return immediately for Tech Lead review; do not commit/push.

## Reopen History

### Reopen 4 - Absent dependency Health map

PMA requested safe map lookup for missing Health, shared by maintained collector and baseline projection, strict Go-template regression for absent/healthy/unhealthy Health, and read-only verification of all seven actual Fedora dependencies. No deployment, restart, credentials/config/Env reads, or commit/push permitted

### Reopen 3 - Executor collector projections

PMA requested replacement only of broad collector Docker inspection with fixed non-secret format projections, preserving sample layout, thresholds, and controller. Same task retained at its existing path for review; no live execution or commit/push is delegated

### Reopen 1 - Atomic mutation and watcher readiness handshake

Prevent watcher rollback during normal startup by using an explicit controller/watchdog phase handshake: pre-start monitoring validates host/dependencies without requiring candidate identity/health, then candidate-active phase enforces exact identity and health after controller confirms startup. Set rollback-required state atomically before selector replacement, so every signal after mutation begins rolls back. Before publishing ready, require watcher alive, no trigger, current phase active, exact identity, and health in one final fail-closed handshake; a watcher trip during final checks must prevent readiness and rollback. Add race tests for startup, final checks, and signal between state write and selector replacement.

### Reopen 2 - Startup resource coverage and atomic ownership

During `pre-start`, enforce candidate container existence plus cgroup memory, growth, OOM-event, restart, and process gates as soon as the container appears, while health remains startup-tolerant. Replace final check-then-act with an atomic ownership protocol: watcher alone transitions a nonce-bound attempt from active to ready, and controller accepts success only if that same nonce is still ready with no rollback/trigger state. Never install the candidate selector during rollback; preserve the prior selector in a separate immutable file and make rollback idempotently restore it. A signal before selector replacement must leave the prior selector untouched. Add tests for startup OOM/growth/restart/process trips, watcher-ready versus rollback race, rollback failure, and pre-selector signal preserving the old selector.

# Post Implementation Task Updates

## Developer Reopen 4: Post Implementation Expectations

Summary: replaced direct optional Health access with `{{with index .State "Health"}}{{json .Status}}{{else}}"none"{{end}}` in both fixed scalar templates. Absent healthcheck produces `none`; unhealthy remains `unhealthy`, never healthy. Added `WATCHDOG_COMMAND_TEST=dependency-baseline` using the identical maintained dependency format and prior TSV order to avoid executor template duplication

Work Performed: strict `text/template` tests use `missingkey=error` on absent, healthy, and unhealthy maps for both templates. Exact-command mocks updated. Both full suites, generated syntax, ShellCheck, and diff checks pass. Read-only SSH fixed projection succeeded for all seven real Fedora dependencies; Qdrant returned `none`, other six `healthy`, all running/restart 0/OOM false

Acceptance Criteria Coverage: AC-1 through AC-4 regression gates pass; renewed AC-5 reviewer approval pending. Logs: `10-reopen4-health-tests.log` and `11-reopen4-fedora-projections.md` in task evidence

Documentation Impact: task-local baseline invocation documented; no runtime source, controller, thresholds, credentials, or product configuration changed. Unrelated orchestrator changes preserved

Open Risks: read-only projections do not qualify the candidate or authorize deployment. Baseline generation must replace the failed partial digest, using a fresh complete successful pipeline

Recommended Next Step: immediate review, then executor regenerates scripts and obtains a fresh baseline with the tested maintained template. No commit or push performed

## Tech Lead Reopen 3: Post Implementation Expectations

- Summary: PASS, bounded collector projection correction approved
- Work performed: inspected the two-file source diff and all generated Docker inspection sites, including child collector command seams and the seven-dependency loop. Every inspection supplies a fixed scalar format; no Env, whole Config, whole Labels, or whole inspect object is fetched. Controller and rollback remain unchanged
- Acceptance criteria coverage: AC-1 PASS full suites and generated Bash syntax/ShellCheck; AC-2 PASS unchanged failure and threshold handling; AC-3 PASS full controller rollback/signal matrix; AC-4 PASS fixed container/image/dependency projections, unchanged 43-field output and dependency TSV ordering, exact-command success/error/timeout tests; AC-5 PASS renewed technical closure and authorization after non-force push
- Documentation impact: task-local evidence only; no steady-state product or CodeMap changes
- Open risks: isolated contract verification is not live Fedora qualification. Known unrelated 14 StaticEng normalization files remain unstaged and preserved
- Recommended next step: executor is authorized immediately after this closure push to continue the existing TASK-006 direct-admin diagnosis under unchanged fresh preflight, exact identity, OOM, one-request/deadline, rollback, full Fedora gates, and soak controls. No deployment or credential/request use occurred in review. NAS remains deferred until fully successful Fedora and separate activation

## Developer Reopen 3: Post Implementation Expectations

- Summary: collector now requests only nine scalar container fields, two scalar image fields, and seven scalar dependency fields using literal Docker `--format` templates
- Work performed: removed broad-object retrieval/filtering, retained per-field parsing and dependency TSV ordering, and used the same projections in collector command-test seams. Image ID/source label are obtained in one projected read
- AC-1: PASS, full controller/watchdog suites and generated syntax; maintained files pass ShellCheck
- AC-2: PASS, existing failure handling and thresholds preserved
- AC-3: PASS, full startup/signal/rollback regression suite unchanged and passing
- AC-4: PASS, mocks require exact command flags, templates, and dependency subjects; success tests verify projected values and timeout/error tests reject command mismatch
- AC-5: pending renewed independent approval; prior approval below applies to Reopen 2 only
- Documentation impact: task-local evidence only; no controller, rollback, threshold, output schema, product documentation, or CodeMap change
- Open risks: this validates isolated command contracts, not live Fedora qualification
- Recommended next step: immediate reviewer approval of the two-file source diff and `logs/08-reopen3-projections.log`. No live deployment, credentials, commit, or push performed; unrelated normalizations preserved

## Developer: Post Implementation Expectations

### Summary

Implemented the complete one-file Fedora candidate startup controller at `.staticeng/evidences/TASK-2026-09-04-005-fix-deployment-controller/harness/fedora-maintenance-controller.sh`. It validates itself and the approved watcher, rollback, and collector before atomic selector replacement, uses only the fixed allowlisted Docker container projection, and rolls back every post-selector startup or watcher-arm failure

### Work Performed

- Added the complete selector, candidate recreation, bounded startup validation, and real-watchdog arm flow in one governed file
- Reused the TASK-002/003 watcher and rollback by exact attempt-local paths and validates their syntax plus exact production rollback wiring before mutation
- Added fail-closed ERR, signal, startup, watcher, and abnormal-exit handling with explicit rollback-failure propagation
- Added one isolated startup-health failure test using a temporary selector and stubbed Docker/curl commands; the mock watcher is armed then stopped, rollback runs exactly once, the rollback selector is restored, and credential/request state remains untouched
- Ran full-file `bash -n`, ShellCheck, the isolated behavior test, `git diff --check`, and StaticEng validation
- Performed no Fedora/NAS access or mutation, credential use, request, service action, runtime-source change, commit, or push

### Acceptance Criteria Coverage

- **AC-1: PASS.** The complete controller is one file and the controller/test pass Bash syntax and ShellCheck
- **AC-2: PASS.** Every fallback uses valid explicit fail-closed shell syntax; no compact `||{...}` or `&&{...}` remains
- **AC-3: PASS.** Isolated startup-health failure arms then terminates the watcher, invokes rollback once, restores the rollback selector, preserves the credential fixture, sends no request, and publishes no ready marker
- **AC-4: PASS.** Controller, watcher, rollback, collector, prerequisites, and exact wiring are validated before selector replacement; the test enforces validation-before-Docker mutation
- **AC-5: PENDING.** Tech Lead review, commit, and immediate TASK-006 Reopen 9 remain outside Developer authority

### Documentation Impact

No product, architecture, technical, or CodeMap documentation change is required because this is a one-off governed maintenance controller and does not alter steady-state runtime source or behavior

### Open Risks

The controller hands off only after bounded healthy startup and real watcher arming. The diagnostic request, full functional gates, and 900-second soak remain governed by TASK-006. Tech Lead must review host attempt paths and execute only under the fresh Reopen 9 authorization

### Recommended Next Step

Tech Lead should review and rerun the controller syntax, ShellCheck, and isolated startup-failure test, then commit and immediately execute TASK-006 Reopen 9 if approved

### Signed Handoff

[Agent Message] From: developer To: product_manager

TASK-2026-09-04-005 AC-1 through AC-4 PASS. The complete one-file controller validates itself plus the approved watcher, rollback, collector, prerequisites, and exact rollback wiring before selector replacement. All fallback syntax is valid and fail closed. The isolated startup-health failure test arms then terminates the watcher, invokes rollback exactly once, restores the rollback selector, preserves the credential fixture, creates no request marker, and publishes no ready marker. Full-file Bash syntax, ShellCheck, diff check, and StaticEng validation pass. No Fedora/NAS access or mutation, credential use, request, runtime-source change, commit, or push occurred. Route immediately to Tech Lead for AC-5 review/commit and TASK-006 Reopen 9

## Tech Lead: Review 1

### Summary

REJECT. Syntax, ShellCheck, fallback form, pre-selector script validation, and the isolated startup-failure rollback test pass. The controller still has functional and rollback-control races, so AC-5 cannot close and TASK-006 Reopen 9 is not authorized

### Findings

- The controller starts the production watcher before its startup poll, but that approved watcher immediately trips rollback on `health != healthy`, readiness not 200, or liveliness not 200. A normally starting candidate can therefore be rolled back on the watcher's first sample, before the controller's 180-attempt startup allowance can operate
- The last watcher liveness check occurs before container inspection and two health requests. If the watcher trips during those checks, the controller can still publish `candidate-ready`, mark handoff complete, and exit zero after rollback has started
- `mutation_started` is set only after the selector replacement command returns. A trapped signal after the atomic replacement but before that assignment exits without invoking rollback and can leave the candidate selector installed

### Acceptance Criteria Coverage

- **AC-1: PASS.** Independent full-file `bash -n` and ShellCheck pass
- **AC-2: PASS.** The reviewed fallback syntax is valid
- **AC-3: PASS.** The isolated startup-failure path invokes rollback once without credential change or request marker
- **AC-4: PARTIAL.** Validation precedes selector replacement and the watcher launch precedes startup polling, but the production watcher and controller startup contracts are behaviorally incompatible
- **AC-5: FAIL.** Commit, closure, and TASK-006 Reopen 9 authorization are withheld because functional and rollback risk remains

### Documentation Impact

No product, architecture, technical, or CodeMap documentation change is required for this rejected review

### Open Risks

An immediate normal-startup rollback, a false ready handoff after watchdog-triggered rollback, or a selector left changed by the post-replacement signal gap could invalidate control of the next Fedora attempt

### Recommended Next Step

Developer should make startup observation compatible with the unchanged watcher safety contract, require a final live watcher and no-rollback gate immediately before handoff, and arm rollback state before selector replacement. Add isolated regression coverage for all three paths, then return the same task for review

### Signed Handoff

[Agent Message] From: tech_lead To: product_manager

TASK-2026-09-04-005 REJECTED FOR FUNCTIONAL AND ROLLBACK RISK. The controller passes syntax, ShellCheck, fallback, and isolated startup-failure checks, but the unchanged watcher can roll back a normally starting candidate before the startup poll completes. The controller can also publish readiness after the watcher has tripped during health checks, and a signal between selector replacement and rollback-state arming can leave the changed selector installed. No commit, push, deployment, credential use, or request occurred. TASK-006 Reopen 9 is not authorized

## Developer Reopen 1: Post Implementation Expectations

### Summary

Implemented the explicit controller/watcher phase handshake. The real watcher now starts in `pre-start`, where it retains host, dependency, protected-state, kernel-OOM, deadline, and rollback-confidence monitoring without applying candidate identity or health gates. The controller advances it to `active` only after bounded exact candidate startup passes, and the active phase restores every approved candidate threshold unchanged

### Work Performed

- Extended the approved watcher generator with atomic `pre-start` and `active` phase files, pre-start acknowledgement, active exact-state acknowledgement, and watcher-owned ready publication
- Set `rollback-required` atomically before selector replacement and armed EXIT/signal rollback before the state transition, closing the post-replacement signal gap
- Made the final handoff require live watcher, absent trigger, active phase, watcher-owned ready acknowledgement, exact candidate manifest/config, healthy state, and readiness/liveliness 200
- Ensured watcher trip removes ready/active state before invoking the unchanged exact rollback, so a final-check race cannot produce a successful handoff
- Added isolated normal-startup, startup-failure, final-check race, and TERM-between-rollback-state-and-selector tests; all preserve credentials and send no request
- Reran the complete approved watcher regression matrix, complete controller tests, full-file Bash syntax, ShellCheck, diff check, and StaticEng validation
- Performed no Fedora/NAS access or mutation, credential use, request, service action, runtime-source change, commit, or push

### Acceptance Criteria Coverage

- **AC-1: PASS.** Complete controller and watcher generator/scripts pass Bash syntax and ShellCheck
- **AC-2: PASS.** All controller/watcher fallbacks remain valid and fail closed
- **AC-3: PASS.** Startup failure, final-check trip, and signal-gap tests each invoke exact rollback with no credential or request consumption
- **AC-4: PASS.** Controller/watcher validation precedes mutation; pre-start monitoring is acknowledged before mutation; active exact-state and ready handshakes follow verified startup
- **AC-5: PENDING.** Tech Lead review, commit, and immediate TASK-006 Reopen 9 remain outside Developer authority

### Documentation Impact

No product, architecture, technical, or CodeMap documentation update is required. The phase protocol is task-local operational control captured in governed evidence rather than steady-state runtime behavior

### Open Risks

The controller still intentionally hands off before the diagnostic request, full functional gates, and 900-second soak. Those remain TASK-006 responsibilities under the existing watcher and rollback controls

### Recommended Next Step

Tech Lead should review the pre-start/active/ready protocol, rerun both complete harness suites, then commit and immediately execute TASK-006 Reopen 9 only on PASS

### Signed Handoff

[Agent Message] From: developer To: product_manager

TASK-2026-09-04-005 REOPEN 1 AC-1 through AC-4 PASS. The watcher now acknowledges pre-start host/dependency protection without candidate identity/health gates, switches to active only after exact healthy startup, and owns final ready publication from a passing active sample. Rollback-required is atomically armed before selector replacement, and any signal thereafter rolls back. Normal startup, startup failure, final-check trip, and signal-between-state-and-selector tests pass with unchanged credentials and zero requests. The complete approved watcher regression matrix, full-file Bash syntax, ShellCheck, diff check, and StaticEng validation pass. No Fedora/NAS access or mutation, credential use, request, runtime-source change, commit, or push occurred. Route to Tech Lead for AC-5 review/commit and TASK-006 Reopen 9

## Tech Lead: Reopen 1 Review

### Summary

REJECT. The complete controller and watcher suites, Bash syntax, ShellCheck, diff check, and StaticEng validation pass. Three functional/OOM/rollback races remain, so AC-5 cannot close and TASK-006 Reopen 9 is not authorized

### Findings

- The watcher stays in `pre-start` from before selector mutation through the entire candidate startup poll. Its pre-start collector exits before reading candidate cgroup memory, cgroup OOM events, restart, or candidate process growth, and the corresponding absolute/delta OOM gates run only in `active`. A starting candidate can therefore exceed the required 8 GiB or three-sample 512 MiB/s gates before health becomes ready
- The final handoff remains an unlocked check-then-act sequence. Watcher `trip` removes ready/active state before publishing the trigger, while the controller separately reads ready, liveness, trigger, phase, and active fields, then performs one last trigger check before setting `handoff_complete=1`. A trip beginning after that check, or between active-state reads and trigger publication, can still produce controller success while rollback is underway. The `final_race` test trips before ready publication and does not cover this final interval
- On a signal after `rollback-required` is armed but before selector replacement, `run_rollback` moves the prepared candidate selector into `.env` and only then invokes rollback. If rollback fails, the signal path leaves the candidate selector installed even though forward selector mutation had not occurred. The signal test covers only successful rollback

### Acceptance Criteria Coverage

- **AC-1: PASS.** Full controller and generated watcher syntax plus ShellCheck pass
- **AC-2: PASS.** Fallback syntax remains valid and fail closed on covered paths
- **AC-3: PARTIAL.** Covered startup, early trip, and successful signal rollback paths preserve credentials and send no request, but the rollback-failure signal path is unsafe
- **AC-4: PARTIAL.** Validation and pre-start acknowledgement precede mutation, but full candidate OOM protection is not active during startup and the final watcher handoff is not race-safe
- **AC-5: FAIL.** Commit, closure, push, and TASK-006 Reopen 9 authorization are withheld

### Documentation Impact

No product, architecture, technical, or CodeMap documentation change is required for this rejected review

### Open Risks

Candidate startup can escape the mandatory cgroup OOM limits, the controller can report success during a watcher-owned rollback, and a pre-selector signal plus rollback failure can install the candidate selector

### Recommended Next Step

Keep candidate cgroup/OOM controls active during startup while deferring only identity and health rejection, serialize watcher trip and final handoff through one ownership/lock protocol, and remove candidate-selector installation from the pre-replacement rollback path. Add exact regressions for startup OOM, a trip at the final handoff boundary, and rollback failure after the pre-selector signal

### Signed Handoff

[Agent Message] From: tech_lead To: product_manager

TASK-2026-09-04-005 REOPEN 1 REJECTED FOR OOM AND ROLLBACK RISK. Full controller and watcher tests pass, but pre-start disables candidate cgroup OOM limits throughout startup, final readiness is still an unlocked check-then-act race, and a pre-selector signal installs the candidate selector before rollback, leaving it installed if rollback fails. No commit, push, deployment, credential use, or request occurred. TASK-006 Reopen 9 is not authorized

## Developer Reopen 2: Post Implementation Expectations

### Summary

Completed the remaining startup resource, ownership, and rollback-selector corrections after inspecting the cancelled resume's existing edits. Unrelated StaticEng normalizations are preserved

### Work Performed

Pre-start now collects container/cgroup/process values through the normal collector and runs the unchanged memory, growth, OOM, restart, PID, FD, CPU, and host/dependency gates. Health requests are deferred until active. Missing container/process instrumentation remains a lost sample under the existing bounded allowance. Candidate first-sample OOM events are checked against zero, not accepted as a new baseline. Runtime image identity uses the frozen config digest rather than the registry manifest digest

Watcher ready publication and rollback transition share one ownership lock and a frozen attempt nonce. Only a passing active watcher sample publishes ready. The controller accepts the same nonce while holding the lock and checking watcher liveness, active phase, and absent rollback intent/trigger/start/completion. Rollback intent is published before waiting for the lock. Selector replacement also checks ownership under that lock, preventing replacement after rollback has won ownership

The prior selector is captured once in an exclusive mode-0400 file and validated against the exact prior reference. Rollback restores only that snapshot and never installs the prepared candidate selector. The controller keeps rollback responsibility armed through return; signal handling consults the durable rollback-required marker even before its in-memory assignment completes

### Acceptance Criteria Coverage

- AC-1: PASS, full maintained Bash syntax, generated-script syntax, and ShellCheck
- AC-2: PASS, fail-closed ownership and rollback branches with no candidate installation during rollback
- AC-3: PASS, startup failure, rollback failure, pre-selector signal, and rollback failure before any restore all preserve expected selector/credential state with no diagnostic request
- AC-4: PASS, startup resource trips, health-tolerant startup, generated watcher nonce readiness, stale-nonce rejection, rollback intent precedence, and rollback after ready but before controller acceptance are covered
- AC-5: PENDING independent Tech Lead review and execution decision

### Documentation Impact

Operational protocol and verification evidence updated here and in the task evidence summary. Product/runtime documentation and CodeMaps do not require changes for this task-local harness correction

### Open Risks

Tests are isolated, not a Fedora qualification. Exact host-side collector projections, fresh preflight/backup, live diagnosis, full functional gates, and soak remain execution gates. NAS promotion is conditional on Fedora fully working per the latest PMA message; no NAS action is performed or authorized by this implementation handback alone

### Recommended Next Step

Immediate Tech Lead review of Reopen 2 and its retained full-suite log, then the governed Fedora diagnosis on approval. No deployment, credentials, runtime-source changes, commit, or push were performed

## Tech Lead: Post Implementation Expectations

### Summary

PASS Reopen 2. The previous startup resource, readiness ownership, and pre-selector signal findings are closed within the functional review boundary

### Work Performed

Reviewed exact controller, watcher generator, rollback snapshot restoration, and both suites. Independently ran both full suites, maintained/generated Bash syntax, ShellCheck, diff whitespace, and StaticEng validation. Candidate startup now retains cgroup absolute/growth/OOM/restart/process limits while health remains startup-tolerant. Runtime identity uses the exact config digest. Watcher-owned nonce readiness and rollback state share a lock, with rollback intent checked before selector replacement and ready acceptance. Pre-selector signals discard the candidate temporary file; even failure before rollback restore preserves the old selector

### Acceptance Criteria Coverage

AC-1 PASS: full-file syntax and ShellCheck. AC-2 PASS: valid fail-closed branches. AC-3 PASS: startup failure, rollback failure, pre-selector TERM, and failure-before-restore tests preserve expected selector and credential state with zero diagnostic requests. AC-4 PASS: validation before mutation, startup resource gates, active exact identity/health, stale nonce rejection, rollback intent precedence, and rollback after ready before acceptance. AC-5 PASS: technical closure approved for commit/non-force push and immediate original-session TASK-006 Reopen 9 authorization, not execution by this reviewer

### Documentation Impact

Task and operational evidence updated; no steady-state product or CodeMap change is required. Existing unrelated StaticEng path normalizations in 12 evidence summaries and two older task files were inspected and preserved, excluded from this controller closure commit

### Open Risks

This is harness approval, not live Fedora qualification. Fresh protected backup/restore, exact signed identity, allowlisted host collector projections and proof, one-request deadline/counters/drain, full functional gates, and continuous 900-second soak remain mandatory execution gates. Nonfunctional hardening is deferred per PO. NAS follows only fully successful Fedora and its separate PMA activation; no NAS deployment is authorized here

### Recommended Next Step

Original execution session may immediately resume TASK-006 Reopen 9 after the closure push, under the existing direct-admin diagnostic controls. No deployment, host access, credential use, or diagnostic request occurred in this review
