# Closure and historical workflow dispositions

PMA's TASK-2026-09-05-003 acceptance closes the final functional repair/deployment scope. Historical results remain attached to the exact artifact/attempt that produced them. Supersession removes an obsolete workflow entry, not a failed assertion, rejected candidate or security requirement from history

## Archived accepted tasks

| Task | Disposition |
| --- | --- |
| TASK-2026-09-05-001-repair-fedora-runtime | done/; final functional/memory repair accepted, all earlier failed attempts/reopens retained |
| TASK-2026-09-05-002-fix-nas-functional-residuals | done/; final AC-1 through AC-6 repair evidence accepted, external peer and finite-window limitations retained |
| TASK-2026-09-01-004-deploy-lazymcp-oauth-nas | done/; initial deployment and final residual repair jointly accepted for scoped functionality; historical unchecked/partial gates remain, unused recovery is not a new rollback PASS |
| TASK-2026-09-05-003-close-dual-host-repair | done/; PMA-authorized documentation-only closure and synchronization |

## Superseded current-workflow entries

These fifteen original task files stay at their stable .staticeng/tasks/todo/ paths to preserve references and full bodies. Their frontmatter now says superseded and points to the closure task. They are removed from Active/Blocked, not entered as new completed qualification passes

| Task | Historical result retained / why no longer active |
| --- | --- |
| TASK-2026-09-01-001-qualify-lazymcp-oauth-release | Rejected older candidate; missing gates and its exact-subject vulnerability finding are not rewritten or attributed to the final image |
| TASK-2026-09-01-002-design-dual-host-release | Design-only PASS for an earlier candidate; later approved repair/deployment path completed |
| TASK-2026-09-01-005-review-release-qualification | Earlier rejection remains valid for its exact candidate; not a current runtime blocker |
| TASK-2026-09-01-007-spec-upstream-main-integration | Historical specification PASS retained; later SCR amendments and final accepted execution resolve its workflow role |
| TASK-2026-09-01-008-design-upstream-main-integration | Historical architecture handoff retained; its pre-integration worktree/merge blockers are not current repair state |
| TASK-2026-09-01-011-qualify-upstream-isolated-candidate | All reopens preserved; Reopen 6 PASS applies to its earlier exact builder/final image, not the final 0c800953 digest |
| TASK-2026-09-03-002-review-fedora-release-readiness | Original REJECT and later exact-subject authorization preserved; no fresh final-image security review inferred |
| TASK-2026-09-03-003-verify-fedora-schema-upgrade-rollback | Earlier isolated schema upgrade/rollback-startup PASS preserved; not a new full production restore rehearsal |
| TASK-2026-09-03-004-sign-attest-release-images | Earlier signatures/attestations remain valid evidence for their recorded subjects; no transfer to the final image |
| TASK-2026-09-03-005-spec-fedora-maintenance-investigation | Historical specification PASS; later explicit no-automatic-rollback direction superseded that execution policy |
| TASK-2026-09-03-016-investigate-internal-user-login | Historical supported email-login finding preserved; no fresh DCR lifecycle or maintenance-client PASS inferred |
| TASK-2026-09-03-006-diagnose-fedora-candidate-live | All failed/stopped/rollback attempts preserved; accepted repair tasks supersede its unavailable-runtime and retry instructions |
| TASK-2026-09-03-008-prepare-fedora-dcr-credential | Failed credential preparation remains failed; later authorized direct probes replaced that one-run prerequisite |
| TASK-2026-09-01-012-release-upstream-main-fedora | Failed candidate deployment and verified historical rollback preserved; later repaired deployment is a distinct result |
| TASK-2026-09-01-003-deploy-lazymcp-oauth-fedora | Initial deployment rejected; accepted later repair does not turn that attempt into a PASS |

## Preserved open work

TASK-2026-08-28-009-define-resilient-lazymcp-discovery remains Active. All unrelated Todo and older blocked backlog entries remain unchanged. TASK-2026-09-03-018-fix-dcr-maintenance-client remains explicitly blocked/deferred with its failed experimental DCR qualification and no retry authorization; this closure does not repair or qualify it

The four pre-existing watchdog artifacts listed in logs/excluded-artifacts.sha256 are not edited, staged, committed, removed or refactored. Their parent evidence/task records and unrelated pending-commit registry rows are not opportunistically cleaned up
