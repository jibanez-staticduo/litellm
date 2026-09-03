# TASK-2026-09-01-011 Reopen 2 Evidence Summary

## Summary

REJECT. The exact clean commit `9374aae27c93d509a12f167c6bb1f83815ed3db1` does not build with its committed Dockerfile defaults. The exact `linux/amd64` builder stopped at the first frozen `uv sync` because the rolling Wolfi repository supplied Python `3.13.15-r4`, whose `math` extension requires `GLIBC_2.44`, while the commit's immutable Wolfi base supplies glibc 2.43. No exact builder image or final candidate was emitted, so the governing stop condition blocks runtime, SBOM, scan, signature, attestation, and promotion gates

Production was queried only with the two Reopen 2 allowlisted formats. Its identity, image, running/healthy state, restart count, and OOM state were identical before and after cleanup. No production Compose, environment, configuration, mounts, credentials, data, or Docker `.Config` were read, and no production object was changed

## Work Performed

- Verified a clean detached `/tmp/opencode` worktree at the exact requested commit, its approved merge parent `0573332425de92ad8f17f6eb3196fce0d3ce7f22`, and an empty tracked/untracked diff
- Created a uniquely named Docker-container BuildKit builder and attempted the exact committed `linux/amd64` `builder` target with source-revision and task labels
- Observed exact package selection and failure: `python-3.13-base 3.13.15-r4` on the committed Wolfi base cannot import `math` because `GLIBC_2.44` is unavailable
- Confirmed causality with a disposable non-candidate probe that changed only the build-base argument to the previously reviewed glibc 2.44 Wolfi digest; the builder target completed, proving the committed default base is the discriminating input. The probe image was not treated as the candidate and was deleted
- Removed both BuildKit builders, their containers and caches, the diagnostic builder image, the pulled PostgreSQL image, temporary metadata, and both detached worktrees. No task-labelled container, network, volume, image, builder, or worktree remains
- Recorded the secret-free command/result ledger in `logs/02-reopen2-build-reject-cleanup.md`
- Ran `staticeng_validate`; all source directories and hierarchy checks passed with zero warnings

## Acceptance Criteria Coverage

- **AC-1: FAIL.** Source commit and ancestry are exact and clean, but its committed build inputs cannot emit the exact builder or final image, so no immutable candidate identities can be retained
- **AC-2: UNVERIFIED.** No isolated PostgreSQL/config/catalog stack, model request, Responses request, MCP/LazyMCP flow, DCR flow, audience test, initialize, or registered-tool test ran after the mandatory build gate failed
- **AC-3: UNVERIFIED.** No candidate exists for health, migration, permission, upstream-auth, inventory, reconnect, log, or preservation gates
- **AC-4: UNVERIFIED.** No exact builder or final subject exists for SBOMs, same-database scans, signatures, attestations, provenance verification, or Critical/High disposition
- **AC-5: PASS FOR SAFETY AND REJECTION EVIDENCE.** Production remained identical and healthy under allowlisted observation, all disposable resources were destroyed, no secret-bearing production source was read, and this rejection packet is secret-free. No push, publication, deployment, mutable tag, Fedora action, or NAS production mutation occurred

## Documentation Impact

Product, architecture, technical, test, and CodeMap documentation are not changed because no product/source behavior or source structure changed. The integration preservation records should be corrected in the follow-up because they claim the adopted upstream Wolfi base preserves a build contract that this exact build disproves

## Open Risks

- The integration merge changed both root Dockerfile Wolfi defaults from the previously reviewed coherent glibc 2.44 digest to an immutable glibc 2.43 base while retaining Python `3.13.15-r4` from a rolling repository
- The current build is not reproducible as a coherent package closure because digest-pinned base files are combined with mutable rolling APK indexes
- All candidate runtime and supply-chain qualifications remain absent; TASK-012 promotion and deployment must remain blocked

## Recommended Next Step

PMA should reopen the source integration or route an approved packaging correction. Restore a reviewed coherent immutable Wolfi/package closure, create a new exact source commit, then rerun TASK-011 from the beginning. Do not override the base only during release construction because that would produce a candidate from uncommitted build inputs

## Signed Handoff

[Agent Message] From: qa_engineer To: product_manager

REJECT. Exact commit `9374aae27c93d509a12f167c6bb1f83815ed3db1` fails its exact builder target because Python `3.13.15-r4` requires `GLIBC_2.44` but the committed Wolfi base supplies glibc 2.43. No exact builder/final image exists, so behavioral and supply-chain gates are fail-closed. Every disposable resource was destroyed, and production identity and health remained unchanged under only the allowlisted observations
