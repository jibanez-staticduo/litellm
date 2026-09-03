# TASK-2026-09-03-002 Evidence Summary

## Summary

REJECT Fedora deployment. The exact Reopen 6 source, builder, final image, security artifacts, functional qualification, cleanup, current fork main, and current Fedora baseline are coherent. Release cannot proceed because no approved StaticDuo signer exists, no immutable registry manifest/config/signature/attestation chain exists, current-Fedora upgrade and prior-image compatibility across ten new migrations are unproved, and no fresh protected DB backup/restore unit exists

## Work Performed

- Verified local and remote fork main at `445877a1243b10af2457a2f363cc54d6b31208a9`; qualified source `bf58974a935521fa570fa7e280c51a00b2e5b54e` is its direct parent and later changes affect StaticEng evidence only
- Verified retained amd64 builder `sha256:eb673f1c4f02a3c0e9cf93d2b73703308664276aea50ea6a57c759956a3788ac` and final `sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915` carry the exact source/task labels
- Recomputed all 21 Reopen 6 evidence checksums and parsed all four machine-readable Grype scans; builder and final each have zero Critical and zero High under the frozen database
- Rechecked cleanup: zero task containers, networks, volumes, builders, and worktrees remain; both exact release images remain available locally
- Traced `cosign.pub` to unchanged upstream BerriAI provenance, checked non-secret local/repository signer metadata, and found no approved StaticDuo signer or executable Cosign installation
- Captured current Fedora identity, health, dependencies, protected hashes/modes, Compose rendering, model/fallback fingerprints, MCP status counts, backup-tool capability, rollback-image availability, and release-artifact inventory through read-only secret-safe probes
- Compared current Fedora source with the candidate and identified ten new migrations; reviewed evidence and found only empty-database/idempotent migration testing, not the required current-schema upgrade and prior-image compatibility test
- Ran `staticeng_validate`; result PASS with zero warnings

## Acceptance Criteria Coverage

- **AC-1: PASS.** Exact source, retained images, labels, qualification artifacts, security scan results, cleanup, and production preservation are verified
- **AC-2: FAIL.** Signing/attestation is mandatory and no approved executable StaticDuo signer is available
- **AC-3: FAIL.** Publication and rollback contracts are frozen, but registry manifests/config linkage/signatures/attestations, migration rollback compatibility, and a fresh DB backup/restore unit do not yet exist
- **AC-4: PASS FOR DEFINITION.** Full Fedora gates and 900-second soak are frozen in the task; execution remains prohibited
- **AC-5: PASS.** Signed verdict is REJECT and all work was read-only/secret-safe with no production, registry, image, container, DB, config, or NAS mutation

## Exact Identities

```text
fork main: 445877a1243b10af2457a2f363cc54d6b31208a9
qualified source: bf58974a935521fa570fa7e280c51a00b2e5b54e
qualified source tree: 5bb1b3185d25ba851482ee022503178996df3341
qualified builder config: sha256:eb673f1c4f02a3c0e9cf93d2b73703308664276aea50ea6a57c759956a3788ac
qualified final config: sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915
Fedora rollback selector: docker.staticduo.com/litellm@sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04
Fedora rollback config: sha256:0a221cc57c07ae89e5a0223488351ff85ac30053771b22b43a94b3aa5361ae42
repository cosign.pub SHA-256: ff8869bf14ba9d10af7b64b9d479543b44daec0165e715753c43ff8a998f6dd3
```

## Documentation Impact

Product and CodeMap documentation are not required. This investigation changes no product behavior or maintained source structure

## Open Risks

- No approved fork release signer or verification identity
- No registry manifest/config/signature/attestation chain
- Ten candidate migrations lack current-Fedora upgrade and prior-image compatibility evidence
- No fresh owner-only DB dump/list/checksum/restore rehearsal
- Deployment behavior and 15-minute production soak remain unexecuted

## Recommended Next Step

PMA should route signer approval and isolated current-schema upgrade/prior-image compatibility as blocking prerequisites. After both pass, request Tech Lead reauthorization and activate TASK-012 for exact publication, fresh backup, Fedora-only digest deployment, complete post-deploy gates, and 900-second soak. NAS and stable remain untouched

## Signed Handoff

[Agent Message] From: tech_lead To: product_manager

REJECT FEDORA DEPLOYMENT. Qualification passes for the exact retained source and images, and current Fedora is stable with a usable immutable rollback selector. Missing approved StaticDuo signing identity, absent registry digest/signature/attestation chain, unproved current-schema upgrade and prior-image compatibility, and absent fresh verified DB backup block release. Keep TASK-012, publication, signing, Fedora, stable, and NAS blocked until those prerequisites pass and Tech Lead reauthorizes. No mutation occurred
