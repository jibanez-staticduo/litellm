---
id: TASK-2026-09-03-005-spec-fedora-maintenance-investigation
complexity: standard
track: spec
slice: foundation
status: superseded
superseded_by: TASK-2026-09-05-003-close-dual-host-repair
supersession_note: Historical maintenance specification PASS retained; later explicit no-rollback repair direction supersedes its execution policy.
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-01-012-release-upstream-main-fedora
assigned_to: business_analyst
handoff_from: product_manager
reopened_count: 0
---

# Task: Specify Fedora maintenance investigation

## Objective

Amend the approved release contract for a user-authorized Fedora maintenance window in which the exact signed candidate may remain deployed while the real-tool timeout and unhealthy transition are diagnosed and corrected.

## Acceptance Criteria

- [x] AC-1: Record explicit Product Owner authorization for a multi-hour Fedora maintenance window and temporary service degradation.
- [x] AC-2: Preserve exact candidate identity, protected backup, rollback readiness, NAS isolation, secret handling, and no mutable tags.
- [x] AC-3: Define investigation safety boundaries, observability allowed, stop/rollback conditions, and maximum maintenance duration.
- [x] AC-4: Require root-cause evidence and candidate/full regression verification before declaring success.
- [x] AC-5: Require immediate rollback on data-integrity risk, uncontrolled resource exhaustion, security regression, or inability to restore health within the authorized window.

## Handoff

[Agent Message] From: product_manager To: business_analyst

The user explicitly authorizes deploying the exact signed candidate to Fedora and investigating live for several hours because Fedora has no important inference workload during this maintenance window. Amend the existing SCR operational acceptance contract only; do not weaken data-integrity, security, backup, rollback, NAS-isolation, exact-digest, or final verification gates. Update this task and SCR with a signed handoff. Do not edit source/tests, deploy, or mutate hosts.

## Clarification

[Agent Message] From: product_manager To: business_analyst

PMA confirms a maximum maintenance duration of 4 hours measured from candidate deployment until either full verification succeeds or mandatory rollback begins. Add intermediate stop gates: immediate rollback for data/security/uncontrolled exhaustion; mandatory decision checkpoint at 2 hours; mandatory rollback by 4 hours if no approved healthy outcome. Complete the SCR amendment/task handoff now. No host/source mutation.

# Post Implementation Task Updates

## Business Analyst: Post Implementation Expectations

### Summary

Amended the approved upstream integration SCR with a Fedora-only live maintenance investigation contract. The amendment records the Product Owner's four-hour authorization, accepts only bounded temporary degradation, and retains every exact-identity, data, security, backup, rollback, NAS-isolation, and final-verification gate

### Work Performed

Recorded the exact signed candidate manifest, config, source, and expected rollback digest; defined the maintenance clock, allowed secret-safe observability, correction governance, the mandatory two-hour continue-or-rollback checkpoint, immediate critical stop conditions, the hard four-hour rollback deadline, root-cause evidence, complete candidate verification, and full rollback verification. No source, tests, Git refs, registry, image, deployment, database, Fedora, or NAS mutation was performed

### Acceptance Criteria Coverage

- **AC-1: PASS.** The SCR records direct Product Owner authorization dated 2026-09-04 for one Fedora-only maintenance window of at most four hours and explicitly limits accepted degradation to a bounded diagnostic state rather than a release outcome
- **AC-2: PASS.** The amendment freezes the exact signed manifest, config, source, and rollback identities; requires a fresh protected database backup and isolated restore verification; prohibits mutable tags, secret or payload retention, automatic database restore, and all NAS mutation
- **AC-3: PASS.** The amendment limits diagnosis to bounded secret-safe observability across LiteLLM, database pool, MCP transport, upstream `defend`, dependencies, and host resources; it adds an evidence-backed two-hour decision and a hard four-hour deadline
- **AC-4: PASS.** Success requires correlated root-cause evidence, classification of the responsible layer, exact approved artifact identity, every original Fedora functional and preservation gate, stable resources, and the complete 900-second soak with final rerun
- **AC-5: PASS.** Immediate rollback is mandatory for data-integrity or security risk, secret exposure, uncontrolled exhaustion, loss of observability or rollback confidence, unauthorized drift, NAS impact, or inability to finish health restoration and full verification within the remaining window. Rollback is also mandatory by four hours without a recorded fully healthy PASS

### Documentation Impact

Updated `.staticeng/docs/scrs/SCR-2026-09-01-001-upstream-main-integration.md` as the existing approved operational source of truth. No SCR registry, product overview, feature list, architecture, technical, or CodeMap update is required because the amendment changes only a time-bounded release investigation authorization and adds no steady-state product behavior

### Open Risks

The live timeout and unhealthy transition remain unexplained until the implementation task captures correlated evidence. Any correction beyond the unchanged exact candidate and already approved selector operation still requires the smallest separate governed task, review, qualification, signing, and release authorization. A four-hour window does not waive or shorten the final 900-second soak, so rollback must start early enough to preserve the hard deadline if full success is no longer credible

### Recommended Next Step

PMA should accept this specification amendment, keep the failed release task blocked, and activate `TASK-2026-09-03-006-diagnose-fedora-candidate-live` only after Tech Lead confirms the read-only-first diagnostic plan, fresh protected backup and restore gate, exact identities, rollback readiness, checkpoint evidence format, and four-hour timer

## Signed Handoff

[Agent Message] From: business_analyst To: product_manager

SCR `SCR-2026-09-01-001-upstream-main-integration` now authorizes one Fedora-only maintenance investigation using exact signed candidate `docker.staticduo.com/litellm@sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3`. The four-hour clock starts at candidate deployment. Immediate rollback applies to data-integrity, security, secret-exposure, uncontrolled resource-exhaustion, observability, rollback-confidence, unauthorized-drift, NAS-impact, and remaining-time stop conditions. At two hours, Tech Lead must record an affirmative continue decision or begin rollback. By four hours, the complete original verification contract, root-cause evidence, and 900-second soak must have a recorded PASS, or exact prior-digest rollback must begin. Fresh protected backup and isolated restore, no mutable tags, no automatic database restore, no ad-hoc correction, full rollback verification, and absolute NAS isolation remain mandatory. This specification task performed no source, registry, deployment, database, Fedora, or NAS mutation
