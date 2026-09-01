# TASK-012 Evidence Summary

## Summary

Implemented exactly the Tech Lead-approved root `Dockerfile` substitutions: both uv sync commands now select `/usr/bin/python3.13`, and the final Prisma assertion explicitly invokes `/app/.venv/bin/python`

## Acceptance Criteria Coverage

- **AC-1: PASS.** Tech Lead approval, portability assumptions, and exact substitution boundaries are recorded in the task
- **AC-2: PASS.** The bounded task diff contains exactly two absolute uv selector substitutions and one explicit venv Prisma assertion substitution (`.staticeng/evidences/TASK-2026-08-31-012-pin-venv-system-python/logs/01-exact-task-diff.log`)
- **AC-3: PARTIAL, TASK-006 GATES DEFERRED.** Static checks preserve Python pins, runtime PATH, absent `VIRTUAL_ENV`, Rust OCI contract, `ENTRYPOINT`, and `CMD`. Per authorization, no complete build, ABI/import/linkage verification, normal-entrypoint run, or runtime smoke was performed (`.staticeng/evidences/TASK-2026-08-31-012-pin-venv-system-python/logs/02-diff-check-and-static-contracts.log`)
- **AC-4: PASS.** Lock/Cargo fingerprints and the seven preserved manifest fingerprints match. No TASK-012 implementation edit was made outside root `Dockerfile`; no production or deployment operation occurred (`.staticeng/evidences/TASK-2026-08-31-012-pin-venv-system-python/logs/04-patches-and-preserved-scope.log`)
- **AC-5: READY FOR INDEPENDENT REVIEW.** Replacement Dockerfile, ordered eight-path manifest, application patch, and combined patch fingerprints are recorded for Tech Lead recomputation (`.staticeng/evidences/TASK-2026-08-31-012-pin-venv-system-python/logs/03-fingerprints-and-eight-path-manifest.log`, `.staticeng/evidences/TASK-2026-08-31-012-pin-venv-system-python/logs/04-patches-and-preserved-scope.log`)

## Verification

`git diff --check` and all bounded static contract assertions passed. Pre-change Dockerfile SHA-256 was `30e2932754e61078f28401daac7029c4cdf4b591a67cceca551139ab1b6ed03c`; post-change SHA-256 is `ab60e645a484ac96b3d43fa23575b9f6aed30f39799bb17e28d1b54dfbe17fbc`

The replacement ordered eight-path manifest SHA-256 is `7b385506ab41f401bb1b6f925611fa3ba793884ea84db8bf3d6c9ff7bb534337`. The application-only patch remains `6d063a7429514d8600a8fbec9c6847f249e20961481fdbad949d41196767f557`; the replacement combined tracked binary patch is `712f8bb20e3a3681694cd523c819d2c9fcfb6a2a99be015f12aee41a75fcf7da`

`staticeng_validate` remains blocked by the known pre-existing missing-CodeMap inventory. The required repair dry-run confirmed that unresolved items require unrelated module-boundary decisions, so no repair was applied (`.staticeng/evidences/TASK-2026-08-31-012-pin-venv-system-python/logs/05-staticeng-validation.log`)

## Documentation Impact

Product and steady-state architecture documentation are not required. This correction restores the intended copied-venv interpreter contract without changing public behavior, navigable source, or CodeMap commands

## Open Risks

The complete candidate build and runtime gates remain unexecuted by explicit authorization. Venv linkage, Python ABI, Prisma, uvloop, Rust bridge, normal entrypoint, and runtime PATH behavior still require TASK-006 Reopen 3 after independent Tech Lead review. Arm64 remains unauthorized

## Recommended Next Step

Tech Lead should independently recompute the replacement fingerprints and inspect the exact three-substitution diff before PMA considers reopening TASK-006

## Tech Lead Independent Review

PASS. The exact three substitutions, Dockerfile fingerprint, ordered eight-path manifest, combined tracked patch, unchanged application-only patch, parser, Python lock, Cargo fingerprints, and preserved runtime contract independently reproduce (`.staticeng/evidences/TASK-2026-08-31-012-pin-venv-system-python/logs/06-tech-lead-independent-review.log`)

TASK-012 is technically accepted. TASK-006 Reopen 3 is authorized only for the exact frozen amd64 inputs and gates recorded in the task. This review does not claim the complete image build, runtime ABI/import behavior, protocol smoke, deployment readiness, arm64 compatibility, or production promotion
