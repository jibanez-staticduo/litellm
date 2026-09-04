---
id: TASK-2026-09-03-023-amend-functional-first-maintenance
complexity: tiny
track: spec
slice: foundation
status: done
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-03-006-diagnose-fedora-candidate-live
assigned_to: business_analyst
handoff_from: product_manager
reopened_count: 0
---

# Task: Amend functional-first maintenance

## Objective

Record the Product Owner direction to prioritize functional validation and Fedora diagnosis, deferring non-blocking security/hardening findings to final reporting.

## Acceptance Criteria

- [x] AC-1: Functional gates are Docker lifecycle, cleanup, Fedora health, models, Responses, MCP/LazyMCP, real tool, memory stability, and soak.
- [x] AC-2: Keep only immediate data-integrity, credential-exposure, uncontrolled OOM, rollback-confidence, and NAS-isolation stop gates.
- [x] AC-3: Defer non-runtime supply-chain and defense-in-depth findings to final reporting; do not let them create additional pre-functional reopen loops.
- [x] AC-4: Permit one final disposable run after bounded source review, then proceed to Fedora maintenance if it functionally passes and cleans up.
- [x] AC-5: Preserve exact digest, fresh backup, watchdog, rollback, four-hour deadline, and no NAS deployment.

## Handoff

[Agent Message] From: product_manager To: business_analyst

The user explicitly directs us to focus on functionality and report security topics at the end. Amend the SCR accordingly: do not waive data integrity, secret exposure, OOM, rollback or NAS-isolation controls, but defer supply-chain and defense-in-depth findings that do not prevent functional execution. Authorize one final disposable run after a bounded review of the current canonical-digest fix, with no further harness hardening loop unless it causes functional failure, resource leak, data risk, or secret exposure. Complete immediately; no runtime mutation.

# Post Implementation Task Updates

## Business Analyst: Post Implementation Expectations

### Summary

PASS. Amended the approved SCR to make the remaining disposable and Fedora maintenance work functional-first while retaining the explicit safety and operational boundaries

### Work Performed

- Bounded the canonical RepoDigest review to exact registry, repository, full digest, config, platform, version, and focused equivalent/wrong-subject tests
- Authorized the one final disposable invocation to proceed to Docker lifecycle, cleanup, health, models, Responses, MCP/LazyMCP, DCR/audience, real-tool, and memory-stability validation after that review passes
- Limited immediate safety stops to data-integrity risk, secret exposure, uncontrolled OOM risk, loss of backup or rollback confidence, and loss of NAS isolation or preservation; resource leaks justify correction when they cause functional failure or uncontrolled OOM risk
- Deferred other non-runtime supply-chain and defense-in-depth findings to the final report without another pre-functional hardening loop
- Preserved exact dependency and Fedora candidate identities, fresh backup and isolated restore verification, watchdog, rollback, two-hour checkpoint, hard four-hour deadline, 900-second soak, and the NAS deployment prohibition
- Performed documentation-only work with no Docker, registry, host, service, database, Fedora, NAS, or other runtime mutation

### Acceptance Criteria Coverage

- **AC-1: PASS.** The SCR names Docker lifecycle and cleanup, Fedora health, models, Responses, MCP/LazyMCP, exact-resource DCR/audience behavior, one authorized real tool, bounded memory stability, and the continuous 900-second soak as the remaining functional gates
- **AC-2: PASS.** The only immediate safety stops are data-integrity risk, secret exposure, uncontrolled OOM risk, loss of backup or rollback confidence, and NAS isolation or preservation failure
- **AC-3: PASS.** Other non-runtime supply-chain and defense-in-depth findings must be captured with evidence and follow-up in the final report and cannot trigger another pre-functional hardening loop
- **AC-4: PASS.** Exactly one final disposable invocation remains authorized after bounded canonical-digest review; a functional and cleanup pass permits direct progression to the already authorized Fedora maintenance path
- **AC-5: PASS.** Exact digest identities, fresh backup and restore proof, watchdog, rollback, two-hour checkpoint, hard four-hour deadline, 900-second soak, and no NAS deployment remain mandatory

### Documentation Impact

Updated `.staticeng/docs/scrs/SCR-2026-09-01-001-upstream-main-integration.md`, this task, task registries, and task evidence. No product overview, feature list, architecture, technical, or CodeMap update is required because this amendment changes only the one-run release-maintenance decision policy, not steady-state product behavior

### Open Risks

The disposable authorization is still consumed by its single invocation and cannot be retried. A functional failure prevents Fedora progression, and cleanup remains mandatory. The functional-first direction does not waive exact identity, backup, watchdog, rollback, deadline, data, secret, resource, or NAS isolation controls

### Recommended Next Step

PMA should route the bounded canonical RepoDigest review, then direct the one final disposable invocation. On a functional and cleanup PASS, proceed to TASK-006 Fedora maintenance under the preserved safeguards and report deferred non-runtime findings at final closure

### Signed Handoff

[Agent Message] From: business_analyst To: product_manager

TASK-023 PASS. The SCR now prioritizes the final disposable and Fedora functional gates. Complete only the bounded canonical RepoDigest review, then run the one authorized disposable lifecycle; if functionality and cleanup pass, proceed to Fedora maintenance. Immediate safety stops are limited to data integrity, secret exposure, uncontrolled OOM risk, rollback-confidence loss, and NAS isolation or preservation. Resource leaks justify correction when they cause functional failure or uncontrolled OOM risk. Defer other non-runtime supply-chain and defense-in-depth findings to the final report without more pre-functional hardening loops. Exact digests, fresh backup and restore proof, watchdog, rollback, two-hour checkpoint, four-hour deadline, 900-second soak, and no NAS deployment remain mandatory. No runtime mutation occurred
